from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def clear_avito_url(raw_url: str) -> str:
    parsed = urlparse(raw_url)
    params = parse_qs(parsed.query)

    # Отрезаем мусорный контекст и метки приложений
    params.pop('context', None)
    params.pop('utm_source', None)
    
    # Принудительно выставляем сортировку по свежести (s=104)
    params['s'] = ['104']

    # Собираем чистую строку обратно
    clean_query = urlencode(params, doseq=True)
    clean_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        clean_query,
        parsed.fragment
    ))
    return clean_url
