import geocoder
import toml
import tweepy
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from wordcloud import WordCloud

# abrir o arquivo com as credenciais de acesso
with open('config.toml') as config:
  config = toml.loads(config.read())
  APP_NAME = config['APP_NAME']
  API_KEY = config['API_KEY']
  API_KEY_SECRET = config['API_KEY_SECRET']
  ACCESS_TOKEN = config['ACCESS_TOKEN']
  ACCESS_TOKEN_SECRET = config['ACCESS_TOKEN_SECRET']

# função para autenticação do usuário
auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
# função para acesso ao app com os tokens
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
# autenticação na API do Twitter
api = tweepy.API(auth)

# Verificando as localizações disponíveis para o trends
available_loc = api.available_trends()
df = pd.json_normalize(available_loc)
df.head(3)
# Filtrando Brasil nas localizações disponíveis
df.query('country == "Brazil"')
# Definindo a localização
loc = geocoder.osm('Brazil')
# Buscando o id da localização baseado na lat e long
closest_loc = api.closest_trends(loc.lat,loc.lng)
# Montando dataset do Top trends da localização informada
trends = api.get_place_trends(closest_loc[0]['woeid'])
# Exibindo os Top Trends Brasil
df_trends = pd.json_normalize(trends[0]['trends'])

# Salvando a Data e Hora Atual
now = datetime.now()

# Organizando o Data frame pelos maiores numeros de Tweets
df_trends = df_trends.sort_values(by = 'tweet_volume', ascending=False)

# Removendo Duplicatas
df_trends = df_trends.drop_duplicates(subset=['name'])

# Criando plot em grafico de barras para os top 5 trends com mais tweets

top5trendsName = df_trends["name"].head(5)
top5trendsTweets = df_trends["tweet_volume"].head(5)

fig = plt.figure(figsize=(10, 4))

# criando o plor de barras
plt.bar(top5trendsName, top5trendsTweets, color='#1d9bf0',
        width=0.5)

for i in range(len(top5trendsName)):
        plt.text(i, top5trendsTweets.iloc[i]//2, int(top5trendsTweets.iloc[i]), ha = 'center')


plt.xlabel("Nome das Trends", fontweight='bold')
plt.ylabel("Numero de Tweets", fontweight='bold')
plt.title("Top 5 Trends com mais Tweets no Brasil - " + now.strftime("%d/%m/%Y às %H:%M:%S"), fontweight='bold')
plt.show()


# eliminando as colunas com valores ausentes
df_trends = df_trends[df_trends['tweet_volume'].notna()]

# Organizando o Data frame decrescente de Tweets para crescente
df_trends = df_trends.sort_values(by = 'tweet_volume')

# criando coluna de crescimento direto dos valores
df_trends['crescimento_direto'] = df_trends['tweet_volume'].pct_change()

# criação de uma lista com o crecimento direto comparado com os numeros dos tweets das trends
listCresTrends = [10]
for x in range(len(df_trends['tweet_volume'])-1):
    seq = int(listCresTrends[x] + (((float(df_trends['crescimento_direto'].iloc[x+1]) * 100) * listCresTrends[x])/100))
    listCresTrends.append(seq)

# criação de um texto com as palavras repetidas baseadas nos Numeros dos tweets das trends
texto = ''
for x in range(len(listCresTrends)):
    for y in range(listCresTrends[x]):
        texto += str(df_trends['name'].iloc[x]) + ' '

# criando e gerando a imagem word cloud com base nos numeros dos tweets das trends:
wordcloud = WordCloud(collocations=False, background_color="black",
                      width=1600, height=800).generate(texto)

# mostrando a imagem criada:
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()

