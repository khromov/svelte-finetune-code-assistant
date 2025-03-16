import * as fs from 'node:fs/promises';
import * as path from 'path';
import { parse } from 'svelte/compiler';

// Get the file path from command line arguments
const rootDir = process.argv[2];

if (!rootDir) {
    console.error('Please provide a path to a Svelte project.');
    process.exit(1);
}

async function extractCriticalBlocksFromSvelte(fileContents) {
    const ast = parse(fileContents)

    const criticalNodes = []
    let total = 0

    const maxNodeSpan = Math.max(fileContents.length / 10, 30)
    const minNodeSpan = 10

    function traverseHtml(node) {
        if (!node || node.start === null || node.end === null) {
            return
        }

        if (node.type === 'Text') {
            return
        }

        const nodeSpan = node.end - node.start
        if (nodeSpan >= minNodeSpan && nodeSpan <= maxNodeSpan) {
            criticalNodes.push(node)
            total += 1
        }

        if (node.children) {
            node.children.forEach(traverseHtml)
        }

        if (node.type === 'IfBlock') {
            traverseHtml(node.else)
            traverseHtml(node.elseif)
        }

        if (node.type === 'AwaitBlock') {
            traverseHtml(node.pending)
            traverseHtml(node.then)
            traverseHtml(node.catch)
        }

        if (node.type === 'EachBlock') {
            traverseHtml(node.else)
        }
    }

    function selectNode(node) {
        if (!node) {
            return
        }

        const span = node.end - node.start
        if (span >= minNodeSpan && span <= maxNodeSpan) {
            criticalNodes.push(node)
        }
    }

    function mergeNodes(nodes) {
        if (nodes.length === 0) {
            return null
        }

        const first = nodes[0]
        const last = nodes[nodes.length - 1]
        return {
            type: first.type,
            start: first.start,
            end: last.end,
        }
    }

    function traverseScript(node) {
        if (!node) {
            return
        }

        const body = node.content.body
        if (!body) {
            return
        }

        let currType = null
        let currNodes = []
        let currNodeSpanLen = 0

        for (const el of body) {
            const span = el.end - el.start
            switch (el.type) {
                case 'ImportDeclaration':
                case 'ExportNamedDeclaration':
                    if (currType === el.type && currNodeSpanLen + span <= maxNodeSpan) {
                        // We can merge with the previous node
                        currNodeSpanLen += span
                        currNodes.push(el)
                    } else {
                        selectNode(mergeNodes(currNodes))

                        currType = el.type
                        currNodes = [el]
                        currNodeSpanLen = span
                    }
                    break
                case 'FunctionDeclaration':
                    if (currNodeSpanLen > 0) {
                        selectNode(mergeNodes(currNodes))
                        currType = null
                        currNodes = []
                        currNodeSpanLen = 0
                    }
                    selectNode(el)

                    // Try adding the entire function body
                    if (el.type === 'FunctionDeclaration' && el.body) {
                        selectNode(el.body)
                    }

                    // Try adding arg list
                    const firstParam = el.params && el.params[0]
                    const lastParam = el.params && el.params[el.params.length - 1]
                    if (firstParam) {
                        selectNode({
                            type: 'Identifier',
                            start: firstParam.start,
                            end: lastParam.end
                        })
                    }

                    // TODO: Ideally we should recurse into the function body here
                    // But the API is really annoying to work with, and I can't figure out the types,
                    // so we'll just skip it for now
                    
                    // Try adding individual items from the body
                    if (el.body && el.body.type === 'BlockStatement') {
                        for (const st of el.body.body) {
                            if (st.type === 'IfStatement') {
                                selectNode(st)
                                if (st.test) {
                                    selectNode(st.test)
                                }
                                if (st.consequent) {
                                    selectNode(st.consequent)
                                }
                                if (st.alternate) {
                                    selectNode(st.alternate)
                                }
                            } else {
                                selectNode(st)
                            }
                        }
                    }

                    break
                default:
                    if (currNodeSpanLen > 0) {
                        selectNode(mergeNodes(currNodes))
                        currType = null
                        currNodes = []
                        currNodeSpanLen = 0
                    }
                    selectNode(el)
                    break
            }
        }
    }

    traverseHtml(ast.html)
    traverseScript(ast.instance)

    return criticalNodes
}

async function listSvelteFiles(dir) {
    const files = await fs.readdir(dir, { recursive: true });
    return files.filter(file => file.endsWith('.svelte'));
}

async function listTypescriptFiles(dir) {
    const files = await fs.readdir(dir, { recursive: true });
    return files.filter(file => file.endsWith('.ts'));
}

function determineSplit() {
    const rnd = Math.random()
    return rnd < 0.98 ? 'train' : 'test'
}

async function run() {
    // Resolve the full path
    const fullPath = path.resolve(rootDir);
    const files = await listSvelteFiles(fullPath);
    let total = 0
    let success = 0
    let failed = 0
    let totalSamples = 0
    const trainSet = await fs.open('dataset.train.jsonl', 'a')
    const testSet = await fs.open('dataset.test.jsonl', 'a')
    const maxChunkLen = 8000
    for (const file of files) {
        const filePath = path.join(fullPath, file) 
        try {
            const fileContents = await fs.readFile(filePath, { encoding: 'utf-8' })
            const datasetSplit = determineSplit()
            const nodes = await extractCriticalBlocksFromSvelte(fileContents)
            for (const node of nodes) {
                const middleLen = node.end - node.start
                const remaining = maxChunkLen - middleLen

                const prefix = fileContents.slice(Math.max(0, node.start - remaining / 2), node.start)
                const suffix = fileContents.slice(node.end, Math.min(fileContents.length, node.end + remaining / 2))

                const jsonl = JSON.stringify({
                    filePath,
                    prefix,
                    middle: fileContents.slice(node.start, node.end),
                    suffix,
                })
                if (datasetSplit === 'train') {
                    await trainSet.write(jsonl + '\n')
                } else {
                    await testSet.write(jsonl + '\n')
                }
            }
            totalSamples += nodes.length
            success += 1
        } catch (err) {
            // console.error('Error extracting critical blocks from file: ', filePath, err)
            failed += 1
        } finally {
            total += 1
        }
    }

    await trainSet.close()
    await testSet.close()

    console.log('Total files: ', total, 'Total samples:', totalSamples)
    console.log('Success: ', success)
    console.log('Failed: ', failed)
}

run()