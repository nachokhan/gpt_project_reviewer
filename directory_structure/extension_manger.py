def get_extensions_list(languages):
    # Diccionario que mapea los lenguajes/tecnologías con sus extensiones de archivo
    extensions_mapping = {
        "python": ["*.py"],
        "web": ["*.html", "*.js", "*.css"],
        "c": ["*.c", "*.h"],
        "c++": ["*.cpp", "*.h"],
        "java": ["*.java"],
        "c#": ["*.cs"],
        "php": ["*.php"],
        "typescript": ["*.ts"],
        "swift": ["*.swift"],
        "go": ["*.go"],
        "ruby": ["*.rb"],
        "kotlin": ["*.kt"],
        "rust": ["*.rs"],
        "lua": ["*.lua"],
        "perl": ["*.pl"],
        "scripting": ["*.sh", "*.bat"],
        "sql": ["*.sql"],
        "data": ["*.xml", "*.json", "*.yml", "*.yaml"]
    }

    # crear la lista de extensiones basada en los lenguajes proporcionados
    to_add_content = []
    for language in languages:
        to_add_content.extend(extensions_mapping.get(str.lower(language), []))

    return to_add_content
