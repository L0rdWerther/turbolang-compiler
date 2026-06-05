import os
import subprocess

def run_all():
    # 1. Rodar testes unitários
    print("Executando testes unitários...")
    test_result = subprocess.run(['py', '-m', 'unittest', 'discover', 'tests'], capture_output=True, text=True)
    print(test_result.stdout)
    if test_result.stderr:
        print(test_result.stderr)
    
    if test_result.returncode == 0:
        print("[PASS] Testes unitários aprovados.\n")
    else:
        print("[FAIL] Testes unitários falharam.\n")

    # 2. Rodar compilação dos exemplos (já existente)
    examples_dir = 'examples'
    if not os.path.exists(examples_dir):
        print(f"Directory {examples_dir} not found.")
        return

    files = [f for f in os.listdir(examples_dir) if f.endswith('.turbo')]
    
    print(f"Iniciando compilação de {len(files)} exemplos...\n")
    
    for file in files:
        path = os.path.join(examples_dir, file)
        
        # Chama o compilador main.py
        result = subprocess.run(['py', 'main.py', path], capture_output=True, text=True)
        
        # O scope_test.turbo deve falhar
        if file == 'scope_test.turbo':
            if result.returncode != 0:
                print(f"[PASS] {file}: Falha esperada.")
            else:
                print(f"[FAIL] {file}: Deveria ter falhado!")
        else:
            if result.returncode == 0:
                print(f"[PASS] {file}: Compilado com sucesso.")
            else:
                print(f"[FAIL] {file}: Erro na compilação.")
                print(result.stdout)

if __name__ == '__main__':
    run_all()
