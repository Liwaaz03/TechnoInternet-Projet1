import os
import argparse
import sys
import re
import urllib.request
from urllib.parse import urljoin
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def download_file(url, save_path):
    try:
        response = urllib.request.urlopen(url)
        with open(save_path, 'wb') as file:
            file.write(response.read())
    except Exception as e:
        print(f"Erreur lors du téléchargement de {url} : {e}", file=sys.stderr)

def extract(url, regex=None, include_images=True, include_videos=True, save_path=None):
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
    except Exception as e:
        print(f"Erreur lors de la récupération de {url} : {e}", file=sys.stderr)
        return

    # Extraire le chemin de base de l'URL
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{os.path.dirname(parsed_url.path)}"

    # Afficher le chemin de base (comme indiqué dans l'exemple)
    print(f"PATH {save_path or base_url}/")
    ressources = []

    if include_images:
        for img in soup.find_all('img'):
            src = img.get('src')
            alt = img.get('alt', 'N/A')
            if src and (not regex or re.search(regex, src)):  # Appliquer le filtre regex ici
                # Créer l'URL complète de l'image
                full_url = urljoin(url, src)
                # Extraire le nom de fichier de l'image
                filename = os.path.basename(src)
                if save_path:
                    local_path = os.path.join(save_path, filename)
                    download_file(full_url, local_path)
                # Ajouter l'entrée à la liste des ressources avec le chemin local
                ressources.append(f"IMAGE {filename} \"{alt}\"")
                
    if include_videos:
        for video in soup.find_all('video'):
            # Chercher l'attribut src de l'élément vidéo ou le premier <source> si disponible
            src = video.get('src')
            if not src:  # Si pas de src direct, chercher dans les éléments <source>
                source_tag = video.find('source')
                if source_tag:
                    src = source_tag.get('src')
            if src:
                full_url = urljoin(url, src)
                # Ajouter l'entrée à la liste des ressources pour les vidéos
                ressources.append(f"VIDEO {full_url} N/A")

    # Afficher les ressources
    for res in ressources:
        print(res)
def generate(ressources, local_path="mypath"):
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Extracted Resources</title>
    </head>
    <body>
        <h1>Visualisateur</h1>
        <table>
            <tr><th>Type</th><th>Ressource</th><th>Alt</th></tr>
    """
    
    # Ajouter chaque ressource dans la table
    for res in ressources:
        type_, url1, alt = res
        
        # Si l'URL de l'image est relative, ajustez-le pour pointer vers le dossier local
        if type_ == "IMAGE" :
            url = local_path+"/"+url1 # Ajouter 'mypath/' devant l'URL relative
        elif type_ == "VIDEO" :
            url = local_path+"/"+url1
        
        # Ajout des ressources sous forme de lien dans le tableau
        html_template += f"<tr><td>{type_}</td><td><a href='{url}' target='_blank'>{url1}</a></td><td>{alt}</td></tr>"

    html_template += """
        </table>
        <div id="container">
        <button id="carrousell">Carrousell</button>
        <button id="gallerie">Gallerie</button>
        </div>
    </body>
    </html>
    """

    sys.stdout.write(html_template)
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
    parser = argparse.ArgumentParser(description="Extraction et génération de ressources web")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Commande extract-p
    extract_parser = subparsers.add_parser('extract', help="Extraire les ressources et les envoyer vers stdout")
    extract_parser.add_argument('url', help="URL de la page web")
    extract_parser.add_argument('-r', '--regex', help="Filtrer les URLs des ressources", default=None)
    extract_parser.add_argument('-i', '--no-images', action='store_true', help="Ne pas inclure les images")
    extract_parser.add_argument('-v', '--no-videos', action='store_true', help="Ne pas inclure les vidéos")
    extract_parser.add_argument('-p', '--path', help="Répertoire pour sauvegarder les ressources extraites", default=None)

    # Commande genere
    generate_parser = subparsers.add_parser('genere', help="Générer une page HTML avec les ressources extraites")

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
