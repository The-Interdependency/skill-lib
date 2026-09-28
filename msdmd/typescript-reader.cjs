// ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
/** Syntax-only worker. Usage: node typescript-reader.cjs < input.json
 * Input: {path, text}; output: version, declarations, imports, docs, diagnostics.
 * It never loads tsconfig, resolves imports, emits code or executes the target.
 */
'use strict';
const fs = require('node:fs');
const ts = require('typescript');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
if (typeof input.path !== 'string' || typeof input.text !== 'string') throw new Error('Invalid reader input');
const sf = ts.createSourceFile(input.path, input.text, ts.ScriptTarget.Latest, true);
const result = {version: ts.version, declarations: [], imports: [], exports: [], docs: [], comments: [], diagnostics: []};
const span = n => ({start_line: sf.getLineAndCharacterOfPosition(n.getStart(sf)).line + 1,
                    end_line: sf.getLineAndCharacterOfPosition(n.getEnd()).line + 1});
const text = n => n ? n.getText(sf) : null;
const counts = new Map();
const commentPositions = new Set();
const qualify = (parent, name) => parent ? `${parent}.${name}` : name;
function visit(node, owner = '') {
  for (const range of [...(ts.getLeadingCommentRanges(input.text, node.getFullStart()) || []),
                       ...(ts.getTrailingCommentRanges(input.text, node.getEnd()) || [])]) {
    if (!commentPositions.has(range.pos)) {
      commentPositions.add(range.pos);
      result.comments.push({text: input.text.slice(range.pos, range.end),
        start_line: sf.getLineAndCharacterOfPosition(range.pos).line + 1,
        end_line: sf.getLineAndCharacterOfPosition(range.end).line + 1});
    }
  }
  if (ts.isImportDeclaration(node) || ts.isExportDeclaration(node)) {
    if (node.moduleSpecifier && ts.isStringLiteralLike(node.moduleSpecifier)) {
      result.imports.push({module: node.moduleSpecifier.text, kind: ts.isImportDeclaration(node) ? 'import' : 'reexport',
        declaration: text(node), owner, ...span(node)});
    } else if (ts.isExportDeclaration(node) && node.exportClause && ts.isNamedExports(node.exportClause)) {
      for (const item of node.exportClause.elements) {
        result.exports.push({kind: 'local-export', local_name: (item.propertyName || item.name).text,
          exported_name: item.name.text, type_only: !!node.isTypeOnly || !!item.isTypeOnly,
          declaration: text(node), owner, ...span(item)});
      }
    }
  }
  if (ts.isCallExpression(node) && (node.expression.kind === ts.SyntaxKind.ImportKeyword ||
      (ts.isIdentifier(node.expression) && node.expression.text === 'require'))) {
    result.diagnostics.push({code: 'dynamic_module_loading', status: 'dynamic-unresolved', ...span(node)});
  }
  let localOwner = owner;
  let name = node.name && (ts.isIdentifier(node.name) || ts.isStringLiteralLike(node.name)) ? node.name.text : null;
  const kind = ts.SyntaxKind[node.kind];
  const isDecl = name && (ts.isFunctionDeclaration(node) || ts.isClassDeclaration(node) || ts.isInterfaceDeclaration(node) ||
    ts.isTypeAliasDeclaration(node) || ts.isMethodDeclaration(node) || ts.isMethodSignature(node) ||
    ts.isPropertyDeclaration(node) || ts.isPropertySignature(node) || ts.isVariableDeclaration(node) ||
    ts.isEnumDeclaration(node) || ts.isModuleDeclaration(node));
  if (isDecl) {
    localOwner = qualify(owner, name);
    const ordinal = counts.get(localOwner) || 0; counts.set(localOwner, ordinal + 1);
    // Equal-name overloads use a declaration ordinal; lines are locations only.
    const identity = `${localOwner}#${ordinal}`;
    let carrier = node;
    if (ts.isVariableDeclaration(node)) carrier = node.parent.parent;
    const exported = !!carrier.modifiers?.some(m => m.kind === ts.SyntaxKind.ExportKeyword);
    const declaration = {name, qualified_name: localOwner, identity, kind, exported, ...span(node),
      parameters: node.parameters?.map(p => ({name: text(p.name), type: text(p.type), optional: !!p.questionToken,
        rest: !!p.dotDotDotToken, default: text(p.initializer)})) || [],
      returns: text(node.type), decorators: (ts.canHaveDecorators(node) ? ts.getDecorators(node) : [])?.map(text) || []};
    result.declarations.push(declaration);
    for (const doc of carrier.jsDoc || []) {
      result.docs.push({identity, owner: localOwner, ...span(doc), text: text(doc),
        description: typeof doc.comment === 'string' ? doc.comment : (doc.comment || []).map(c => c.text || '').join(''),
        tags: (doc.tags || []).map(t => ({tag: t.tagName.text, text: text(t), name: text(t.name),
          type: text(t.typeExpression), comment: typeof t.comment === 'string' ? t.comment : null}))});
    }
  }
  ts.forEachChild(node, child => visit(child, localOwner));
}
visit(sf);
for (const binding of result.exports) {
  const qualified = qualify(binding.owner, binding.local_name);
  const declarations = result.declarations.filter(item => item.qualified_name === qualified);
  binding.declaration_identities = declarations.map(item => item.identity);
  for (const declaration of declarations) {
    declaration.exported = true;
    declaration.export_names = [...new Set([...(declaration.export_names || []), binding.exported_name])];
  }
}
for (const d of sf.parseDiagnostics) result.diagnostics.push({code: `typescript_${d.code}`, status: 'invalid',
  message: ts.flattenDiagnosticMessageText(d.messageText, '\n'),
  start_line: sf.getLineAndCharacterOfPosition(d.start || 0).line + 1,
  end_line: sf.getLineAndCharacterOfPosition((d.start || 0) + (d.length || 0)).line + 1});
process.stdout.write(JSON.stringify(result));
// ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
