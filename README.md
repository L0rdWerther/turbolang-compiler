# Compilador TurboLang

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

Arte ASCII baseada em: https://ascii.co.uk/art/formula1

## Visão Geral

TurboLang é um compilador que traduz código-fonte da linguagem TurboLang para assembly SaM (*Simple Abstract Machine*). O projeto foi desenvolvido manualmente, sem geradores automáticos de lexer/parser, e possui temática inspirada em F1 e WRC.

### Funcionalidades

* Lexer manual
* Parser por descida recursiva
* AST completa
* Tabela de símbolos com escopos
* Análise semântica e verificação de tipos
* Geração de assembly SaM
* Relatórios de erro detalhados
* Sem dependências externas

## Como Executar

```powershell
.\.venv\Scripts\python.exe main.py examples\hello.turbo
.\.venv\Scripts\python.exe main.py examples\hello.turbo -o hello.sam
```

Também é possível usar a interface padrão:

```bash
python main.py programa.turbo
python main.py -v programa.turbo
python main.py programa.turbo -o programa.sam
```

## Como Rodar os Testes

```powershell
.\.venv\Scripts\python.exe -m unittest discover tests
.\.venv\Scripts\python.exe tests\test_all.py
```

Ou:

```bash
python -m unittest discover tests
python -m unittest tests.test_lexer
python -m unittest tests.test_parser
python -m unittest tests.test_semantic
python -m unittest tests.test_codegen
```

## Estrutura do Projeto

```
turbolang-compiler/
│
├── lexer/              # Análise léxica
├── parser/             # Parser e nós da AST
├── semantic/           # Tabela de símbolos e análise semântica
├── codegen/            # Geração de código SaM
├── tests/              # Testes automatizados
├── examples/           # Programas de exemplo
│
├── compiler.py         # Orquestração do compilador
├── main.py             # Interface de linha de comando
├── requirements.txt    # Dependências
└── README.md
```

## Exemplo de Código TurboLang

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

## Tipos Suportados

| Tipo     | Descrição                      | Exemplo         |
| -------- | ------------------------------ | --------------- |
| `int`    | Inteiro                        | `42`            |
| `float`  | Ponto flutuante                | `3.14`          |
| `char`   | Caractere                      | `'a'`           |
| `bool`   | Booleano                       | `true`, `false` |
| `string` | Suporte parcial para impressão | `"hello"`       |

## Recursos da Linguagem

### Variáveis

```turbolang
int x;
float pi = 3.14;
char letra = 'A';
bool ativo = true;

x = 42;
```

### Operadores

A linguagem suporta:

* Aritméticos: `+`, `-`, `*`, `/`, `%`
* Comparação: `==`, `!=`, `<`, `>`, `<=`, `>=`
* Lógicos: `&&`, `||`, `!`

### Controle de Fluxo

```turbolang
if (condicao) {
    print(1);
} else {
    print(0);
}

while (x < 10) {
    x = x + 1;
}

do {
    x = x + 1;
} while (x < 10);

for i = 1 to 10 {
    print(i);
}
```

Também existem aliases em português:

```turbolang
faca {
    print(1);
} enquanto (condicao);

para i = 1 ate 10 {
    print(i);
}
```

### Funções

```turbolang
func somar(int a, int b) -> int {
    return a + b;
}

func main() {
    int resultado = somar(5, 3);
    print(resultado);
}
```

### Função Embutida

```turbolang
print(42);
print("Olá");
print(x + y);
```

## Gramática Resumida

```ebnf
program        → function_decl*
function_decl  → 'func' IDENTIFIER '(' parameters? ')' ('->' TYPE)? block
parameters     → parameter (',' parameter)*
parameter      → TYPE IDENTIFIER

block          → '{' statement* '}'
statement      → var_decl
               | assignment
               | if_stmt
               | while_stmt
               | do_while_stmt
               | for_stmt
               | return_stmt
               | print_stmt
               | expr_stmt
               | block

var_decl       → TYPE IDENTIFIER ('=' expression)? ';'
assignment     → IDENTIFIER ('[' expression ']')? '=' expression ';'
if_stmt        → 'if' '(' expression ')' block ('else' block)?
while_stmt     → 'while' '(' expression ')' block
do_while_stmt  → 'do' block 'while' '(' expression ')' ';'
for_stmt       → 'for' IDENTIFIER '=' expression 'to' expression block
return_stmt    → 'return' expression? ';'
print_stmt     → 'print' '(' expression ')' ';'

expression     → logical_or
logical_or     → logical_and ('||' logical_and)*
logical_and    → equality ('&&' equality)*
equality       → comparison (('==' | '!=') comparison)*
comparison     → additive (('<' | '>' | '<=' | '>=') additive)*
additive       → multiplicative (('+' | '-') multiplicative)*
multiplicative → unary (('*' | '/' | '%') unary)*
unary          → ('!' | '-') unary | postfix
postfix        → primary ('[' expression ']')*
primary        → literal | IDENTIFIER | function_call | '(' expression ')'
```

## Pipeline do Compilador

```
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
Análise Semântica
    ↓
AST validada
    ↓
Gerador de Código
    ↓
Assembly SaM
```

## Fases do Compilador

### 1. Análise Léxica

Transforma o código-fonte em tokens, reconhecendo identificadores, palavras-chave, operadores, delimitadores e literais.

Exemplo:

```text
Entrada: int x = 42;
Tokens:  [INT, IDENTIFIER("x"), ASSIGN, INTEGER(42), SEMICOLON, EOF]
```

### 2. Análise Sintática

Usa descida recursiva para gerar uma AST a partir dos tokens.

### 3. Análise Semântica

Valida a AST e verifica:

* Escopos
* Declarações duplicadas
* Variáveis não declaradas
* Compatibilidade de tipos
* Parâmetros de funções
* Tipos de retorno

### 4. Geração de Código

Percorre a AST validada e gera instruções assembly SaM.

## Assembly SaM

O compilador gera assembly SaM textual. O programa inicia com:

```sam
ADDSP 1
LINK
JSR FUNCAO_main
POPFBR
STOP
```

A função `main` é usada como ponto de entrada obrigatório.

### Convenção de Chamadas

* Argumentos são empilhados da esquerda para a direita.
* Parâmetros usam offsets negativos no frame.
* Variáveis locais usam offsets positivos.
* Funções retornam escrevendo no slot de retorno.
* `JUMPIND` retorna ao chamador.

### Algumas Instruções Usadas

| Instrução                           | Descrição                   |
| ----------------------------------- | --------------------------- |
| `PUSHIMM`                           | Empilha inteiro ou booleano |
| `PUSHIMMF`                          | Empilha float               |
| `PUSHIMMCH`                         | Empilha caractere           |
| `PUSHOFF`                           | Carrega valor do frame      |
| `STOREOFF`                          | Armazena valor no frame     |
| `ADD`, `SUB`, `TIMES`, `DIV`, `MOD` | Operações inteiras          |
| `ADDF`, `SUBF`, `TIMESF`, `DIVF`    | Operações com float         |
| `JUMP`, `JUMPC`                     | Saltos                      |
| `JSR`                               | Chamada de função           |
| `JUMPIND`                           | Retorno de função           |
| `WRITE`, `WRITEF`, `WRITECH`        | Impressão                   |
| `STOP`                              | Fim do programa             |

## Suporte Parcial

Alguns recursos existem parcialmente no projeto, mas não fazem parte do escopo obrigatório completo:

* `string`: suporte principal para literais em `print`
* arrays/vetores: aparecem em partes do parser/codegen, mas não estão completos como recurso obrigatório

## Exemplos

### Olá Mundo

```turbolang
func main() {
    print("Olá, Mundo!");
}
```

### Fibonacci

```turbolang
func fibonacci(int n) -> int {
    if (n <= 1) {
        return n;
    }

    return fibonacci(n - 1) + fibonacci(n - 2);
}

func main() {
    print(fibonacci(10));
}
```

### Fatorial

```turbolang
func fatorial(int n) -> int {
    if (n <= 1) {
        return 1;
    }

    return n * fatorial(n - 1);
}

func main() {
    print(fatorial(5));
}
```

## Testes

A suíte cobre as principais partes do compilador:

* Lexer
* Parser
* Análise semântica
* Geração de código
* Programas de exemplo

Execute tudo com:

```bash
python -m unittest discover tests
```

## Tratamento de Erros

O compilador reporta erros léxicos, sintáticos e semânticos com informações úteis para depuração, como linha, coluna e descrição do problema.

Exemplos de erros detectados:

* String ou caractere não terminado
* Token inesperado
* Variável não declarada
* Função não declarada
* Declaração duplicada
* Incompatibilidade de tipos
* Número incorreto de argumentos
* Retorno inválido

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
JSR FUNCAO_main
POPFBR
STOP

FUNCAO_add:
PUSHOFF -2
PUSHOFF -1
ADD
STOREOFF -3
JUMPIND

FUNCAO_main:
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
JSR FUNCAO_add
POPFBR
ADDSP -2
WRITE
ADDSP -2
JUMPIND
```

## Complexidade

| Fase              | Complexidade |
| ----------------- | ------------ |
| Lexer             | O(n)         |
| Parser            | O(n)         |
| Análise semântica | O(n)         |
| Geração de código | O(n)         |

Onde `n` é o número de tokens do programa.

---

**Autor:** João Henrique R. Lopes
**Versão do Python:** 3.14
