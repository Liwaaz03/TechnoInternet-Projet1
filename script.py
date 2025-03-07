import os
import argparse
import sys
import re
import urllib.request
from urllib.parse import urlparse,urljoin
from bs4 import BeautifulSoup

# Sauvegarder un fichier et retourner le chemin du fichier local
def download_file(url, save_path):
    try:
        response = urllib.request.urlopen(url)

        # Extraire uniquement le nom du fichier depuis l'URL
        filename = os.path.basename(urlparse(url).path)

        # Construire le chemin de sauvegarde correct
        file_path = os.path.join(save_path, filename)

        # Télécharger et sauvegarder le fichier
        with open(file_path, 'wb') as file:
            file.write(response.read())

        return file_path  # Retourner le chemin local du fichier
    except Exception as e:
        print(f"Erreur lors du telechargement de {url} : {e}")
        return None
    
def extract(url, regex=None, include_images=True, include_videos=True, save_path=None):
    try:
        with urllib.request.urlopen(url) as reponse:
            html = reponse.read()
        soup = BeautifulSoup(html, 'html.parser')
    except Exception as e:
        print(f"Erreur lors de la recuperation de {url} : {e}")
        return
    
    print(f"Path {save_path if save_path else url}") # Affichage du chemin du fichier telecharge ou URL
    
    if include_images:
        for img in soup.find_all('img'):
            src = img.get('src')
            alt = img.get('alt', 'N/A')
            if src:
                full_url = urljoin(url, src)
                if regex and not re.search(regex, full_url):
                    continue
                if save_path: #Changer le chemin si on sauvegarde localement
                    os.makedirs(save_path, exist_ok=True)
                    local_filename = download_file(full_url, save_path)
                    if local_filename:
                        print(f"IMAGE {local_filename} \"{alt}\"") # Utiliser le chemin du fichier locale
                else:
                    print(f"IMAGE {full_url} \"{alt}\"") # Utiliser l'URL

    if include_videos:
        for video in soup.find_all('video'):
            # Vérifier l'attribut 'src' dans l'élément <video>
            src = video.get('src')
            
            if not src:  # Si src n'est pas trouvé, chercher dans <source> 
                source = video.find('source')
                if source:
                    src = source.get('src')

            if src:
                full_url = urljoin(url, src)
                if regex and not re.search(regex, full_url):
                    continue
                if save_path:
                    os.makedirs(save_path, exist_ok=True)
                    local_filename = download_file(full_url, save_path)
                    if local_filename:
                        print(f"VIDEO {local_filename} \"N/A\"")
                else:
                    print(f"VIDEO {full_url} \"N/A\"")

def generate(ressources):

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Extracted Resources</title>
        <link rel="stylesheet" href="style.css">
        <script src="output.js" defer></script>
    </head>
    <body>
        <h1>Ressources extraites</h1>
        <table>
            <tr><th>Type</th><th>Resource</th><th>Alt text</th></tr>
    """

    for res in ressources:
        type_, url, alt = res
        html_template += f'<tr><th>{type_}</th><td><a href={url} target=blank> {url}</a></td><td>{alt}</td></tr>' '\n'

    html_template += """
        </table>
        <div id="container">
        <button id="carrousell">Carousell</button>
        <button id="gallerie">Gallerie</button>
        </div>
    </body>
    </html>
    """

    with open('output.html', 'w') as file:
        file.write(html_template)

def parse_extract_output():
    ressources = []
    for line in sys.stdin:
        parts = line.strip().split(' ', 2)
        if len(parts) >= 2:
            type_ = parts[0]
            url = parts[1]
            alt = parts[2] if len(parts) == 3 else 'N/A'
            if type_ in {"IMAGE", "VIDEO"}:
                ressources.append((type_, url, alt))
    return ressources

def main():
    parser = argparse.ArgumentParser(description="Extraire les ressources d'une page web et/ou generer une page HTML")
    subparsers = parser.add_subparsers(dest='command', required=True)

    #Commande extract
    extract_parser = subparsers.add_parser('extract', help="Extraire les ressources d'une page web")
    extract_parser.add_argument('url', help="URL de la page web")
    extract_parser.add_argument('-r', '--regex', help="Filtrer les URLs des ressources")
    extract_parser.add_argument('-i', '--no-images', action='store_true', help="Ne pas inclure les images")
    extract_parser.add_argument('-v', '--no-videos', action='store_true', help="Ne pas inclure les videos")
    extract_parser.add_argument('-p', '--path', help="Directory pour sauvegarder les ressources extraites", default=None)

    #Commande generate
    generate_parser = subparsers.add_parser('genere', help="Generer une page HTML avec les ressources extraites")

    args = parser.parse_args()

    if args.command == 'extract':
        extract(
            args.url,
            args.regex,
            not args.no_images,
            not args.no_videos,
            args.path
        )
    elif args.command == 'genere':
        ressources = parse_extract_output()
        generate(ressources)

if __name__ == '__main__':
    main()
