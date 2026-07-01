# Compilador TurboLang

Compilador para a linguagem **TurboLang**, que traduz código-fonte para assembly **SaM** (*Simple Abstract Machine*). O projeto implementa manualmente as principais fases de compilação: análise léxica, análise sintática, análise semântica e geração de código.

```
                         __
                   _.--""  |
    .----.     _.-'   |/\| |.--.
    |jrei|__.-'   _________|  |_)  _______________  
    |  .-""-.""""" ___,    `----'"))   __   .-""-.""""--._  
    '-' ,--. `    |tic|   .---.       |:.| ' ,--. `      _`.
     ( (    ) ) __|tac|__ \\|// _..--  \/ ( (    ) )--._".-.
      . `--' ;\__________________..--------. `--' ;--------'
       `-..-'                               `-..-'
```
https://ascii.co.uk/art/formula1

## Funcionalidades

* Lexer manual, sem geradores externos
* Parser por descida recursiva
* AST completa para representação do programa
* Tabela de símbolos com escopos
* Verificação semântica e validação de tipos
* Geração de assembly SaM
* Relatórios de erro com linha e coluna
* Sem dependências externas

## Como executar

```powershell
.\.venv\Scripts\python.exe main.py examples\hello.turbo
.\.venv\Scripts\python.exe main.py examples\hello.turbo -o hello.sam
```

Com saída detalhada:

```powershell
.\.venv\Scripts\python.exe main.py -v examples\hello.turbo
```

## Como rodar os testes

```powershell
.\.venv\Scripts\python.exe -m unittest discover tests
.\.venv\Scripts\python.exe tests\test_all.py
```

Também é possível executar testes específicos:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_lexer
.\.venv\Scripts\python.exe -m unittest tests.test_parser
.\.venv\Scripts\python.exe -m unittest tests.test_semantic
.\.venv\Scripts\python.exe -m unittest tests.test_codegen
```

## Estrutura do Projeto

```text
turbolang-compiler/
├── lexer/
│   ├── token.py
│   ├── lexer.py
│   └── keywords.py
├── parser/
│   ├── parser.py
│   └── ast_nodes.py
├── semantic/
│   ├── symbol_table.py
│   ├── type_checker.py
│   └── semantic_analyzer.py
├── codegen/
│   ├── sam_instructions.py
│   └── code_generator.py
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_semantic.py
│   ├── test_codegen.py
│   └── test_all.py
├── examples/
├── compiler.py
├── main.py
├── requirements.txt
└── README.md
```

## Exemplo de programa TurboLang

```turbolang
func soma(int a, int b) -> int {
    return a + b;
}

func main() {
    int x = 10;
    int y = 20;
    int z = soma(x, y);

    if (z > 20) {
        print(z);
    }

    while (x < y) {
        x = x + 1;
    }
}
```

## Linguagem Suportada

### Tipos

| Tipo     | Descrição                      | Exemplo   |
| -------- | ------------------------------ | --------- |
| `int`    | Inteiro                        | `42`      |
| `float`  | Ponto flutuante                | `3.14`    |
| `char`   | Caractere                      | `'a'`     |
| `bool`   | Booleano                       | `true`    |
| `string` | Suporte parcial para impressão | `"hello"` |

### Recursos principais

A linguagem suporta:

* Declaração de variáveis
* Atribuição
* Expressões aritméticas, relacionais e lógicas
* Funções com parâmetros e retorno
* `if` / `else`
* `while`
* `do while`
* `for` contado
* `return`
* `print`

## Gramática resumida

```ebnf
program       → function_decl*
function_decl → 'func' IDENTIFIER '(' parameters? ')' ('->' TYPE)? block
parameters    → parameter (',' parameter)*
parameter     → TYPE IDENTIFIER

block         → '{' statement* '}'
statement     → var_decl
              | assignment
              | if_stmt
              | while_stmt
              | do_while_stmt
              | for_stmt
              | return_stmt
              | print_stmt
              | expr_stmt

var_decl      → TYPE IDENTIFIER ('=' expression)? ';'
assignment    → IDENTIFIER '=' expression ';'
if_stmt       → 'if' '(' expression ')' block ('else' block)?
while_stmt    → 'while' '(' expression ')' block
do_while_stmt → 'do' block 'while' '(' expression ')' ';'
for_stmt      → 'for' IDENTIFIER '=' expression 'to' expression block
return_stmt   → 'return' expression? ';'
print_stmt    → 'print' '(' expression ')' ';'

expression    → logical_or
logical_or    → logical_and ('||' logical_and)*
logical_and   → equality ('&&' equality)*
equality      → comparison (('==' | '!=') comparison)*
comparison    → additive (('<' | '>' | '<=' | '>=') additive)*
additive      → multiplicative (('+' | '-') multiplicative)*
multiplicative → unary (('*' | '/' | '%') unary)*
unary         → ('!' | '-') unary | primary
primary       → literal | IDENTIFIER | function_call | '(' expression ')'
```

## Pipeline de Compilação

```text
Código-fonte
   ↓
Lexer
   ↓
Tokens
   ↓
Parser
   ↓
AST
   ↓
Análise semântica
   ↓
AST validada + tabela de símbolos
   ↓
Geração de código
   ↓
Assembly SaM
```

### Fases

| Fase                 | Função                                        |
| -------------------- | --------------------------------------------- |
| Lexer                | Converte caracteres em tokens                 |
| Parser               | Constrói a AST a partir dos tokens            |
| Analisador semântico | Valida escopos, declarações, chamadas e tipos |
| Gerador de código    | Emite assembly SaM a partir da AST validada   |

## Assembly SaM

O compilador gera código para a variante textual de SaM usada no projeto.

Todo programa inicia com:

```sam
ADDSP 1
LINK
JSR FUNCTION_main
POPFBR
STOP
```

A função `main` é o ponto de entrada obrigatório.

### Convenção de chamada

* Argumentos são empilhados pelo chamador da esquerda para a direita
* Parâmetros usam offsets negativos no frame
* O slot de retorno fica em `-(argc + 1)`
* Variáveis locais usam offsets positivos a partir de `2`
* Funções retornam armazenando valor no slot de retorno e executando `JUMPIND`

### Representação de tipos

| TurboLang | SaM                        |
| --------- | -------------------------- |
| `int`     | Palavra inteira            |
| `bool`    | `0` ou `1`                 |
| `char`    | Código numérico            |
| `float`   | Valor real                 |
| `string`  | Suporte parcial em `print` |

## Exemplo de Assembly Gerado

Entrada:

```turbolang
func add(int a, int b) -> int {
    return a + b;
}

func main() {
    int x = 5;
    int y = 3;
    print(add(x, y));
}
```

Saída SaM:

```sam
ADDSP 1
LINK
JSR FUNCTION_main
POPFBR
STOP

FUNCTION_add:
PUSHOFF -2
PUSHOFF -1
ADD
STOREOFF -3
JUMPIND

FUNCTION_main:
ADDSP 1
ADDSP 1
PUSHIMM 5
STOREOFF 2
PUSHIMM 3
STOREOFF 3
ADDSP 1
PUSHOFF 2
PUSHOFF 3
LINK
JSR FUNCTION_add
POPFBR
ADDSP -2
WRITE
ADDSP -2
JUMPIND
```

## Tratamento de Erros

O compilador reporta erros léxicos, sintáticos e semânticos com informações de linha e coluna.

Exemplos de validações:

* Caracteres inválidos
* Strings ou caracteres não terminados
* Tokens inesperados
* Delimitadores ausentes
* Variáveis ou funções não declaradas
* Declarações duplicadas
* Tipos incompatíveis
* Número incorreto de argumentos
* Retornos inválidos em funções ou procedimentos

## Testes

A suíte cobre:

* Lexer
* Parser
* Análise semântica
* Geração de código
* Programas completos em `examples/`

Execute tudo com:

```powershell
.\.venv\Scripts\python.exe -m unittest discover tests
```

## Observações

* Strings têm suporte limitado a literais usados em `print`.
* Vetores/arrays aparecem em partes do compilador e em exemplos, mas são considerados suporte parcial/opcional.
* O projeto não possui dependências externas.

## Autor

João Henrique R Lopes
