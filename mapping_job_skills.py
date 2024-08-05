import os
import re
import json
import matplotlib.pyplot as plt
from collections import defaultdict

# Caminho para a pasta que contém os arquivos .md
folder_path = './'
json_file_path = 'skills_count.json'

# Função para carregar o JSON existente
def load_skills_count(json_file_path):
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

# Função para salvar o JSON com as skills ordenadas
def save_skills_count(skills_count, json_file_path):
    # Ordenar o dicionário do maior para o menor valor
    sorted_skills_count = dict(sorted(skills_count.items(), key=lambda item: item[1], reverse=True))
    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(sorted_skills_count, file, ensure_ascii=False, indent=4)

# Função para adicionar a tag 'processed' ao arquivo
def add_processed_tag(file_path):
    with open(file_path, 'r+', encoding='utf-8') as file:
        content = file.read()
        if 'tags:' in content:
            header_match = re.search(r'---(.*?)---', content, re.DOTALL)
            if header_match:
                header_content = header_match.group(1)
                if 'processed' not in header_content:
                    new_header_content = re.sub(
                        r'(tags:\s*(?:\s*-\s*\w+\s*)*)',
                        r'\1  - processed\n',
                        header_content,
                        flags=re.DOTALL
                    )
                    new_content = content.replace(header_content, new_header_content)
                    file.seek(0)
                    file.write(new_content)
                    file.truncate()

# Função para verificar se o arquivo já foi processado
def is_processed(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        header_match = re.search(r'---(.*?)---', content, re.DOTALL)
        if header_match:
            header_content = header_match.group(1)
            if 'processed' in header_content:
                return True
    return False

# Função para ler o conteúdo dos arquivos .md
def read_md_files(folder_path, existing_skills):
    job_files = [f for f in os.listdir(folder_path) if f.endswith('.md') and f != 'Mapping job descriptions.md']
    new_skills_count = defaultdict(int)
    
    for job_file in job_files:
        file_path = os.path.join(folder_path, job_file)

        # Verificar se o arquivo já foi processado
        if is_processed(file_path):
            continue
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Verificar as tags no cabeçalho
        header_match = re.search(r'---(.*?)---', content, re.DOTALL)
        if header_match:
            header_content = header_match.group(1)
            tags_match = re.search(r'tags:\s*(.*?)\n', header_content, re.DOTALL)
            if tags_match:
                tags = tags_match.group(1).strip().split('\n')
                if '- reject' in tags:
                    continue
                if '- jobs' not in tags:
                    continue
        
        # Ignorar habilidades específicas e tratar apenas a primeira ocorrência por arquivo
        skills_found = set()
        skills_to_ignore = {'Mapping job descriptions', 'Data Engineering'}
        skills = re.findall(r'\[\[(.*?)\]\]', content)
        for skill in skills:
            if skill in skills_to_ignore:
                continue
            if skill not in skills_found:
                new_skills_count[skill] += 1
                skills_found.add(skill)
        
        # Adicionar a tag 'processed' ao arquivo
        add_processed_tag(file_path)
    
    # Atualizar o dicionário existente com as novas contagens
    for skill, count in new_skills_count.items():
        existing_skills[skill] = existing_skills.get(skill, 0) + count
    
    return existing_skills

# Função para ordenar as skills por frequência
def sort_skills_by_frequency(skills_count):
    sorted_skills = sorted(skills_count.items(), key=lambda item: item[1], reverse=True)
    return sorted_skills

# Função para gerar gráfico das skills
def generate_skills_graph(sorted_skills, top_n=20, output_path='skills_frequency.png'):
    top_skills = sorted_skills[:top_n]
    skills, counts = zip(*top_skills)
    plt.figure(figsize=(10, 6))
    bars = plt.barh(skills, counts, color='skyblue')
    plt.xlabel('Points')
    plt.title('Top {} Skills Frequency'.format(top_n))
    plt.gca().invert_yaxis()
    plt.tight_layout()

    # Adicionar contagem no topo de cada barra
    for bar in bars:
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2, f'{int(width)} pts', 
                 va='center', ha='left', color='black', fontsize=10)

    plt.savefig(output_path)
    plt.show()  # Exibe o gráfico
    plt.close()

# Carregar as skills do JSON existente
existing_skills = load_skills_count(json_file_path)

# Ler os arquivos .md e atualizar as skills
updated_skills_count = read_md_files(folder_path, existing_skills)

# Salvar as skills atualizadas no JSON
save_skills_count(updated_skills_count, json_file_path)

# Ordenar as skills por frequência
sorted_skills = sort_skills_by_frequency(updated_skills_count)

# Gerar gráfico das skills e salvar como imagem
generate_skills_graph(sorted_skills, top_n=20, output_path='skills_frequency.png')

print("Gráfico gerado e salvo como 'skills_frequency.png'.")

