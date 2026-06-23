# Compilador TurboLang

## Resumo para Entrega

TurboLang e um compilador didatico para a disciplina de Compiladores. O objetivo do projeto e traduzir uma linguagem procedural de alto nivel para uma variante textual documentada de assembly SaM.

Requisitos obrigatorios atendidos: funcoes/procedimentos, tipos `int`, `float` IEEE-754 simples/float32 e `char`, variaveis, constantes numericas, atribuicao, operadores aritmeticos, relacionais e logicos, estruturas `if then/entao else/senao`, repeticoes `while`, `do while`/`faca enquanto` e `for`/`para`, analise lexica e sintatica manuais, analise semantica, geracao de codigo, testes e documentacao.

Como executar:

```powershell
.\.venv\Scripts\python.exe main.py examples\hello.turbo
.\.venv\Scripts\python.exe main.py examples\hello.turbo -o hello.sam
```

Como rodar os testes:

```powershell
.\.venv\Scripts\python.exe -m unittest discover tests
.\.venv\Scripts\python.exe tests\test_all.py
```

Limitacoes opcionais conhecidas: strings tem suporte parcial para literais/impressao; vetores/arrays sao parciais/opcionais; operadores bit-a-bit nao foram priorizados porque sao opcionais no PDF; a SaM usada e uma variante textual documentada neste README.

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

## Visão Geral

Este projeto implementa um compilador que traduz código-fonte TurboLang para linguagem assembly SaM (Simple Abstract Machine), inspirado na F1 e WRC (Rally).

### Funcionalidades

- ✅ Implementação manual do lexer (sem geradores de regex)
- ✅ Parser por descida recursiva
- ✅ Representação completa de AST
- ✅ Tabela de símbolos com gerenciamento de escopo
- ✅ Verificação e validação de tipos
- ✅ Geração de código assembly SaM
- ✅ Relatório de erros detalhado ("Pit Stop" reports)
- ✅ Sem dependências externas

## Estrutura do Projeto

```
turbolang-compiler/
│
├── lexer/
│   ├── __init__.py
│   ├── token.py          # Definições de Token e TokenType
│   ├── lexer.py          # Analisador léxico
│   └── keywords.py       # Palavras reservadas
│
├── parser/
│   ├── __init__.py
│   ├── parser.py         # Parser por descida recursiva
│   └── ast_nodes.py      # Definições dos nós da AST
│
├── semantic/
│   ├── __init__.py
│   ├── symbol_table.py   # Tabela de símbolos e gerenciamento de escopo
│   ├── type_checker.py   # Regras de verificação de tipos
│   └── semantic_analyzer.py  # Análise semântica
│
├── codegen/
│   ├── __init__.py
│   ├── sam_instructions.py   # Definições das instruções SaM
│   └── code_generator.py     # Geração de código
│
├── tests/
│   ├── __init__.py
│   ├── test_lexer.py     # Testes do lexer
│   ├── test_parser.py    # Testes do parser
│   ├── test_semantic.py  # Testes do analisador semântico
│   ├── test_codegen.py   # Testes do gerador de código
│   └── test_all.py       # Testa todos os examples e testes
│
├── examples/
│   ├── hello.turbo
│   ├── fibonacci.turbo
│   ├── factorial.turbo
│   ├── array_sum.turbo
|   ├── control_flow.turbo
│   └── ...
│
├── compiler.py           # Orquestração principal do compilador
├── main.py              # Interface de linha de comando
├── requirements.txt     # Dependências (nenhuma!)
└── README.md           # Este arquivo
```

## Especificação da Linguagem

### Sintaxe

#### Estrutura do Programa
```turbolang
func nomeFuncao(param1 tipo, param2 tipo) -> tipoRetorno {
    // corpo da função
}
```

#### Exemplo Básico
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

### Tipos de Dados

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `int` | Número inteiro | `42`, `-5` |
| `float` | Número de ponto flutuante | `3.14`, `2.0` |
| `char` | Caractere único | `'a'`, `'\n'` |
| `bool` | Valor booleano | `true`, `false` |
| `string` | Parcial/opcional: literal para impressao | `"hello"` |

### Variáveis

#### Declaração
```turbolang
int x;
float pi = 3.14;
char letra = 'A';
bool flag = true;
```

#### Atribuição
```turbolang
x = 42;
```

### Constantes

- Inteiro: `42`, `-5`, `0`
- Float: `3.14`, `2.0`, `-1.5`
- Caractere: `'a'`, `'1'`, `'\n'`
- Booleano: `true`, `false`
- String: `"hello"`, `"linha1\nlinha2"` (parcial/opcional; uso principal em `print`)

### Operadores

#### Aritméticos
```
+  (adição)
-  (subtração)
*  (multiplicação)
/  (divisão)
%  (módulo)
```

#### Comparação
```
==  (igual)
!=  (diferente)
<   (menor que)
>   (maior que)
<=  (menor ou igual)
>=  (maior ou igual)
```

#### Lógicos
```
&&  (E lógico)
||  (OU lógico)
!   (NÃO lógico)
```

### Estruturas de Controle

#### Instrução If
```turbolang
if (condicao) {
    // executado se a condição for verdadeira
} else {
    // executado se a condição for falsa
}
```

#### Laço While
```turbolang
while (condicao) {
    // corpo executado enquanto a condição for verdadeira
}
```

#### Laço Do While
```turbolang
do {
    // corpo executado pelo menos uma vez
} while (condicao);
```

Aliases aceitos:
```turbolang
faca {
    // corpo executado pelo menos uma vez
} enquanto (condicao);
```

#### Laço For Contado
```turbolang
for i = 1 to 10 {
    print(i);
}
```

Aliases aceitos:
```turbolang
para i = 1 ate 10 {
    print(i);
}
```

#### Instrução Return
```turbolang
return valor;
```

### Funções

#### Declaração
```turbolang
func somar(int a, int b) -> int {
    return a + b;
}
```

#### Chamada
```turbolang
int resultado = somar(5, 3);
```

### Funções Embutidas

#### print()
```turbolang
print(42);
print("Olá");
print(x + y);
```

## Gramática (EBNF)

```ebnf
program        → (function_decl)*
function_decl  → 'func' IDENTIFIER '(' parameters? ')' ('->' TYPE)? '{' block '}'
parameters    → parameter (',' parameter)*
parameter     → TYPE IDENTIFIER

block         → statement*
statement     → var_decl
               | assignment
               | if_stmt
               | while_stmt
               | do_while_stmt
               | for_stmt
               | return_stmt
               | print_stmt
               | block
               | expr_stmt

var_decl      → TYPE IDENTIFIER ('=' expression)? ';'
assignment    → IDENTIFIER ('['expression']')? '=' expression ';'
if_stmt       → 'if' '(' expression ')' block ('else' block)?
while_stmt    → 'while' '(' expression ')' block
do_while_stmt → 'do' block 'while' '(' expression ')' ';'
for_stmt      → 'for' IDENTIFIER '=' expression 'to' expression block
return_stmt   → 'return' expression? ';'
print_stmt    → 'print' '(' expression ')' ';'
expr_stmt     → expression ';'

expression    → logical_or
logical_or    → logical_and ('||' logical_and)*
logical_and   → equality ('&&' equality)*
equality      → comparison (('==' | '!=') comparison)*
comparison    → additive (('<' | '>' | '<=' | '>=') additive)*
additive      → multiplicative (('+' | '-') multiplicative)*
multiplicative → unary (('*' | '/' | '%') unary)*
unary         → ('!' | '-') unary | postfix
postfix       → primary ('[' expression ']')*
primary       → literal
               | IDENTIFIER
               | function_call
               | '(' expression ')'

function_call → IDENTIFIER '(' arguments? ')'
arguments     → expression (',' expression)*

literal       → INTEGER | FLOAT | STRING | CHAR | 'true' | 'false'

TYPE          → 'int' | 'float' | 'char' | 'bool'
IDENTIFIER    → [a-zA-Z_][a-zA-Z0-9_]*
INTEGER       → [0-9]+
FLOAT         → [0-9]+\.[0-9]+
STRING        → '"' ... '"'
CHAR          → ''' . '''
```

## Fases do Compilador

### Fase 1: Análise Léxica

O lexer converte o código-fonte em um fluxo de tokens.

**Entrada:** String do código-fonte  
**Saída:** Lista de objetos Token  
**Processo:**
- ✅ Varredura caractere por caractere
- ✅ Reconhecimento de palavras-chave, identificadores e literais
- ✅ Rastreamento de número de linha e coluna
- ✅ Relatório de erros para caracteres inválidos

**Exemplo:**
```
Entrada:  int x = 42;
Tokens:   [INT, IDENTIFIER("x"), ASSIGN, INTEGER(42), SEMICOLON, EOF]
```

### Fase 2: Análise Sintática

O parser usa descida recursiva para construir uma Árvore Sintática Abstrata (AST) a partir dos tokens.

**Entrada:** Fluxo de tokens  
**Saída:** AST (nó Program e filhos)  
**Processo:**
- ✅ Parsing por descida recursiva
- ✅ Implementação das regras gramaticais
- ✅ Detecção de erros sintáticos

**Exemplo:**
```
Entrada:  func add(int a, int b) -> int { return a + b; }
Saída:    FunctionDecl(
            name="add",
            parameters=[Parameter("int", "a"), Parameter("int", "b")],
            return_type="int",
            body=Block([
              ReturnStatement(
                BinaryExpression(Identifier("a"), "+", Identifier("b"))
              )
            ])
          )
```

### Fase 3: Análise Semântica

Valida a AST e constrói as tabelas de símbolos.

**Entrada:** AST  
**Saída:** AST anotada (ou erros)  
**Processo:**
- ✅ Análise em duas passagens
  - Passagem 1: Registrar todas as funções
  - Passagem 2: Analisar os corpos das funções
- ✅ Gerenciamento da tabela de símbolos com escopos
- ✅ Verificação de tipos
- ✅ Detecção de declarações duplicadas
- ✅ Detecção de variáveis não declaradas

### Fase 4: Geração de Código

Gera código assembly SaM a partir da AST.

**Entrada:** AST validada  
**Saída:** Código assembly SaM  
**Processo:**
- ✅ Travessia da AST
- ✅ Emissão de instruções
- ✅ Consulta à tabela de símbolos para offsets
- ✅ Geração de rótulos para fluxo de controle

## Instruções Assembly SaM

| Instrução | Operando | Descrição |
|-----------|----------|-----------|
| ADDSP | quantidade | Ajusta o tamanho da pilha |
| LINK | - | Cria o frame da chamada atual |
| POPFBR | - | Restaura o frame anterior apos uma chamada |
| PUSHIMM | valor | Empilha constante inteira/booleana |
| PUSHIMMF | valor | Empilha constante real |
| PUSHIMMCH | caractere | Empilha constante caractere |
| PUSHOFF | offset | Carrega valor por offset do frame |
| STOREOFF | offset | Armazena topo da pilha por offset do frame |
| ADD | - | Soma |
| SUB | - | Subtrai |
| TIMES | - | Multiplica |
| DIV | - | Divide |
| MOD | - | Modulo |
| ADDF | - | Soma reais |
| SUBF | - | Subtrai reais |
| TIMESF | - | Multiplica reais |
| DIVF | - | Divide reais |
| GREATER | - | Maior que |
| LESS | - | Menor que |
| EQUAL | - | Igual |
| CMPF | - | Compara reais |
| ISPOS | - | Testa resultado positivo |
| ISNEG | - | Testa resultado negativo |
| ISNIL | - | Testa resultado zero |
| AND | - | E lógico |
| OR | - | OU lógico |
| NOT | - | NÃO lógico |
| JUMP | rótulo | Salto incondicional |
| JUMPC | rótulo | Salta se o topo for verdadeiro |
| JSR | rótulo | Chama subrotina/função |
| JUMPIND | - | Retorna da função chamada |
| WRITE | - | Imprime inteiro/booleano |
| WRITEF | - | Imprime real |
| WRITECH | - | Imprime caractere |
| STOP | - | Encerra execução |

### Variante SaM usada pelo projeto

O assembly gerado por este compilador usa a mesma variante SaM textual do compilador Portugol de referencia. Cada valor ocupa uma palavra de pilha.

#### Fluxo inicial

O programa sempre inicia com:

```sam
ADDSP 1
LINK
JSR FUNCAO_main
POPFBR
STOP
```

`FUNCAO_main` e o rotulo gerado para a funcao `main`. O bootstrap reserva o slot de retorno, cria o frame, chama `main`, restaura o frame e finaliza com `STOP`.

#### Protocolo de funcao

| Instrucao | Operando | Significado |
|-----------|----------|-------------|
| `ADDSP 1` | - | Reserva o slot de retorno antes de uma chamada |
| `LINK` | - | Inicia o frame da chamada |
| `JSR FUNCAO_nome` | rotulo | Chama a funcao/procedimento |
| `POPFBR` | - | Restaura o frame do chamador |
| `JUMPIND` | - | Retorna ao chamador |

Convencao de frame:

- argumentos sao empilhados pelo chamador da esquerda para a direita;
- parametros usam offsets negativos relativos ao frame, de `-argc` ate `-1`;
- o slot de retorno fica no offset `-(argc + 1)`;
- variaveis locais usam offsets positivos a partir de `2`;
- variaveis locais sao reservadas com `ADDSP 1`;
- funcoes retornam armazenando o valor no slot de retorno e executando `JUMPIND`;
- procedimentos retornam diretamente com `JUMPIND`.

#### Tipos em assembly

| Tipo TurboLang | Representacao |
|----------------|---------------|
| `int` | palavra inteira |
| `bool` | `0` para falso, `1` para verdadeiro |
| `char` | caractere literal, emitido com `PUSHIMMCH` |
| `float` | real emitido com `PUSHIMMF` |
| `string` | suporte parcial para literal em `print`, emitido com `PUSHS`/`WRITES` |

Conversoes e operacoes de ponto flutuante:

- `ITOF` converte uma palavra `int` para `float32`;
- `ADDF`, `SUBF`, `TIMESF`, `DIVF` operam sobre reais;
- comparacoes de reais usam `CMPF` seguido de `ISPOS`, `ISNEG`, `ISNIL` e, quando necessario, `NOT`.

#### Escopo obrigatorio e suporte parcial

Obrigatorio neste projeto:

- lexer, parser, AST e analise semantica para funcoes, variaveis, expressoes, `if`, `while`, `return` e `print`;
- `if (...) then { ... } else { ... }`;
- alias `entao` para `then`;
- alias `senao` para `else`;
- funcoes tipadas exigem retorno em todos os caminhos aceitos pela analise semantica;
- procedimentos rejeitam `return` com valor;
- geracao de assembly com entrada garantida por `main`;
- literais `float` como `float32` IEEE-754;
- literais `char` como codigo numerico.

Parcial/opcional:

- strings tem suporte limitado a literais e impressao; nao ha operacoes completas de string;
- vetores/arrays aparecem em partes do parser/codegen antigo, mas nao estao completos como recurso obrigatorio da linguagem.

## Uso

### Linha de Comando

```bash
# Compilar um arquivo
python main.py programa.nova

# Compilar com saída detalhada
python main.py -v programa.nova

# Salvar saída em arquivo
python main.py programa.nova -o programa.sam

# Combinar opções
python main.py -v programa.nova -o programa.sam
```

### Como Biblioteca

```python
from compiler import compile_file, compile_string

# Compilar a partir de arquivo
result = compile_file('programa.nova', verbose=True)
if result.success:
    print(result.output)
else:
    print(result.error)

# Compilar a partir de string
code = """
func main() {
    print(42);
}
"""
result = compile_string(code, verbose=True)
print(result.output)
```

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
    int resultado = fibonacci(10);
    print(resultado);
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

### Arrays/Vetores (Opcional/Parcial)

Vetores/arrays aparecem em exemplos e partes do compilador, mas sao tratados como suporte parcial/opcional. O requisito obrigatorio do PDF nao depende desse recurso.
```turbolang
func soma_array(int arr, int tamanho) -> int {
    int total = 0;
    int i = 0;
    
    while (i < tamanho) {
        total = total + arr[i];
        i = i + 1;
    }
    
    return total;
}

func main() {
    int arr[5];
    arr[0] = 10;
    arr[1] = 20;
    arr[2] = 30;
    arr[3] = 40;
    arr[4] = 50;
    
    print(soma_array(arr, 5));
}
```

### Fluxo de Controle
```turbolang
func main() {
    int x = 10;
    int y = 20;
    
    if (x < y) {
        print("x é menor que y");
    } else {
        print("x não é menor que y");
    }
    
    while (x < 15) {
        print(x);
        x = x + 1;
    }
}
```

## Testes

Execute a suíte de testes completa:

```bash
# Executar todos os testes
python -m unittest discover tests

# Executar arquivo de teste específico
python -m unittest tests.test_lexer
python -m unittest tests.test_parser
python -m unittest tests.test_semantic
python -m unittest tests.test_codegen

# Executar teste específico
python -m unittest tests.test_lexer.TestLexer.test_integer_literal
```

### Cobertura de Testes

#### Testes do Lexer
- ✅ Literais inteiros e de ponto flutuante
- ✅ Literais de string e caractere
- ✅ Identificadores e palavras-chave
- ✅ Operadores (aritméticos, comparação, lógicos)
- ✅ Delimitadores
- ✅ Rastreamento de linha e coluna
- ✅ Tratamento de erros (strings não terminadas, caracteres inválidos)

#### Testes do Parser
- ✅ Declarações de funções
- ✅ Parâmetros e tipos de retorno
- ✅ Declarações e atribuições de variáveis
- ✅ Estruturas de controle (if, while)
- ✅ Expressões (binárias, unárias)
- ✅ Chamadas de função
- ✅ Tratamento de erros (delimitadores ausentes, erros sintáticos)

#### Testes Semânticos
- ✅ Declaração de variáveis e escopo
- ✅ Verificação e validação de tipos
- ✅ Validação de parâmetros de função
- ✅ Validação do tipo de retorno
- ✅ Detecção de declarações duplicadas
- ✅ Detecção de variáveis não declaradas
- ✅ Validação do tipo da condição (if/while)
- ✅ Verificação de compatibilidade de tipos
- ✅ Validação de programa completo

#### Testes de Geração de Código
- ✅ Geração de programa simples
- ✅ Compilação de literal inteiro
- ✅ Operações aritméticas
- ✅ Fluxo de controle (if/while)
- ✅ Chamadas e retornos de função
- ✅ Compilação de programa completo

**Total atual:** ver saida de `python -m unittest discover tests`.

## Arquitetura

### Padrões de Projeto

- **Padrão Visitor:** Usado para travessia da AST na análise semântica e geração de código
- **Descida Recursiva:** Usado no parser para análise sintática
- **Padrão Tabela de Símbolos:** Usado para gerenciamento de escopo e rastreamento de variáveis
- **Análise em Duas Passagens:** Primeira passagem para declarações, segunda para validação

### Pipeline de Compilação

```
Código-Fonte (entrada.nova)
    ↓
[Lexer] → Tokens
    ↓
[Parser] → AST
    ↓
[Analisador Semântico] → AST Validada + Tabela de Símbolos
    ↓
[Gerador de Código] → Assembly SaM
    ↓
Código Assembly (saida.sam)
```

## Tratamento de Erros

O compilador fornece mensagens de erro detalhadas para:

**Erros Léxicos**
- Strings/caracteres não terminados
- Caracteres inválidos
- Informação de linha/coluna

**Erros Sintáticos**
- Tokens inesperados
- Delimitadores ausentes
- Gramática inválida

**Erros Semânticos**
- Variáveis/funções não declaradas
- Declarações duplicadas
- Incompatibilidade de tipos
- Quantidade incorreta de parâmetros
- Condições de fluxo de controle inválidas

## Exemplo de Assembly Gerado

### Programa de Entrada

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

### Assembly SaM Gerado

```
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

## Características de Desempenho

| Fase | Complexidade | Observações |
|------|-------------|-------------|
| Léxica | O(n) | Passagem única, caractere por caractere |
| Sintática | O(n) | Descida recursiva, passagem única |
| Semântica | O(n) | Duas passagens para declarações e validação |
| Geração de Código | O(n) | Travessia única da AST |

Onde `n` = número de tokens no código-fonte.

---

**Autor:** João Henrique R Lopes

**Versão do Python:** 3.14
