from lxml import html
import requests
import pandas as pd
import time
anime_data = []
st = time.time()
try:
    df = pd.read_csv('i.csv')
    i_start = df.values[0][0]
except:
    i_start = 0

for i in range(1, 1038):
    if i < i_start:
        continue
    url = f'https://shikimori.one/animes/page/{i}'

    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    tree = html.fromstring(response.content)

    # Используем XPath для выбора всех ссылок
    names_ru = tree.xpath('//a')

    names_href = []
    for name in names_ru:
        href = name.get('href')
        if href and 'animes/' in href and 'page' not in href:
            names_href.append(href)

    for name in names_href:
        j = 0
        while True:
            j+=1
            response1 = requests.get(name+'/reviews/page/'+str(j), headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            #print(response1.url)
            if 'page' not in response1.url and j!=1:
                break
            #print(name+'/reviews')
            tree1 = html.fromstring(response1.content)

            # Выбираем все div элементы
            reviews_words = tree1.xpath("//div[contains(@class, 'review-details')]")
            reviews_users_names = tree1.xpath("//div[contains(@class, 'review-details')]/div[contains(@class, 'name-url')]/div[contains(@class, 'name-inner')]/a[contains(@class, 'name')]/text()")

            reviews = []
            #print(len(reviews_words))

            for s in reviews_words:
                s = s.text_content().lower()
                #print(s)
                if 'положительный' in s:
                    reviews.append(1)
                elif 'отрицательный' in s:
                    reviews.append(-1)
                else:
                    reviews.append(0)
            # Печатаем текст каждого div
            #print([review.text_content() for review in reviews if 'G'])
            response_metadata = requests.get(name, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            tree_metadata = html.fromstring(response_metadata.content)
            # Извлекаем все div теги с классом review-info и все элементы внутри
            anime_keys = tree_metadata.xpath("//div[contains(@class, 'line-container')]/div[contains(@class, 'line')]/div[contains(@class, 'key')]/text()")
            anime_values_elems = tree_metadata.xpath("//div[contains(@class, 'line-container')]/div[contains(@class, 'line')]/div[contains(@class, 'value')]")
            anime_values_f = [anime_keys[anime] + anime_values_elems[anime].text_content() for anime in range(len(anime_keys))][:6]
            anime_values = anime_values_f[:4]+anime_values_f[6:]
            anime_genres = 'Жанры: ' + ' '.join(tree_metadata.xpath("//span[contains(@class, 'genre-ru')]/text()"))
            anime_name = tree_metadata.xpath("//h1/text()")
            anime_values.append(anime_genres)

            for s in range(len(reviews_users_names)):
                anime_data.append([reviews_users_names[s], reviews[s]] + anime_name + anime_values)
        #print(anime_data)
    df1 = pd.DataFrame([[i]])
    df1.to_csv('i.csv', index=False, header=False)
    df = pd.DataFrame(anime_data)
    df.to_csv('anime_data.csv', index=False)
        #print(time.time() - st)
    print(i)