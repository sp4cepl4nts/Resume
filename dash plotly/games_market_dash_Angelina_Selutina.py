#!/usr/bin/env python
# coding: utf-8

# In[1]:


import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go


# In[3]:


# Загрузим данные
csv_file_path = 'C:/Users/angel/Downloads/DashboardSeliutina/df1_games.csv'
df = pd.read_csv(csv_file_path)

# Стиль
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Создадим Dash приложение
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Список платформ и жанров для фильтров
platforms = df['Platform'].unique()
genres = df['Genre'].unique()
min_year = df['Year_of_Release'].min()
max_year = df['Year_of_Release'].max()

# Структура дашборда
app.layout = html.Div([
    html.H1('Игровая индустрия 1990-2010'),
    html.Div('Используйте фильтры, выбирая различные платформы, жанры и временные интервалы, и находите закономерности в данных'),
    # Первый ряд - фильтры
    html.Div([
        # Фильтр 1: Платформы
        dcc.Dropdown(
            id='platform-filter',
            options=[{'label': platform, 'value': platform} for platform in platforms],
            multi=True,
            value=platforms.tolist(),
            placeholder="Выберите платформы"
        ),
        
        # Фильтр 2: Жанры
        dcc.Dropdown(
            id='genre-filter',
            options=[{'label': genre, 'value': genre} for genre in genres],
            multi=True,
            value=genres.tolist(),
            placeholder="Выберите жанры"
        ),
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    
    html.Div([
        dcc.RangeSlider(
            id='year-range-filter',
            min=min_year,
            max=max_year,
            step=1,
            marks={year: str(year) for year in range(min_year, max_year + 1, 5)},
            value=[min_year, max_year],
            tooltip={"placement": "bottom", "always_visible": True}
        ),
    ], style={'position': 'absolute', 'top': '10px', 'right': '10px', 'width': '300px'}),

    # Второй ряд - числовые показатели
    html.Div([
        html.Div([
            html.H6('Общее число игр'),
            html.Div(id='total-games', style={'fontSize': 24}),
        ], className="card"),

        html.Div([
            html.H6('Средняя оценка игроков'),
            html.Div(id='avg-user-score', style={'fontSize': 24}),
        ], className="card"),

        html.Div([
            html.H6('Средняя оценка критиков'),
            html.Div(id='avg-critic-score', style={'fontSize': 24}),
        ], className="card"),
    ], style={'display': 'flex', 'justify-content': 'space-between'}),

    # Третий ряд - графики
    html.Div([
        # График 4: Средний возрастной рейтинг по жанрам
        dcc.Graph(id='avg-rating-by-genre'),

        # График 5: Scatter plot с разбивкой по жанрам
        dcc.Graph(id='scatter-plot'),

        # График 6: Stacked area plot по годам и платформам
        dcc.Graph(id='stacked-area-plot'),
    ], style={'display': 'flex', 'justify-content': 'space-between'})
])


def create_avg_rating_by_genre_chart(filtered_df):
    avg_rating_by_genre = filtered_df.groupby('Genre')['Rating'].mean().reset_index()
    
    # Столбчатая диаграмма (Bar chart)
    bar = go.Bar(
        x=avg_rating_by_genre['Genre'], 
        y=avg_rating_by_genre['Rating'], 
        name='Средний рейтинг',
        marker=dict(color='lightblue')
    )
    
    # Линейная диаграмма (Line chart)
    line = go.Scatter(
        x=avg_rating_by_genre['Genre'], 
        y=avg_rating_by_genre['Rating'], 
        mode='lines+markers', 
        name='Линейный тренд',
        line=dict(color='red', width=2),
        marker=dict(color='red', size=5)
    )
    
    # Создаём график с двумя элементами
    fig = go.Figure(data=[bar, line])
    fig.update_layout(
        title="Средний возрастной рейтинг по жанрам",
        xaxis_title="Жанры",
        yaxis_title="Средний рейтинг",
        barmode='group'
    )
    
    return fig




# Обработчик изменения фильтров
@app.callback(
    [
        Output('total-games', 'children'),
        Output('avg-user-score', 'children'),
        Output('avg-critic-score', 'children'),
        Output('avg-rating-by-genre', 'figure'),
        Output('scatter-plot', 'figure'),
        Output('stacked-area-plot', 'figure'),
    ],
    [
        Input('platform-filter', 'value'),
        Input('genre-filter', 'value'),
        Input('year-range-filter', 'value'),
    ]
)
def update_dashboard(platforms_selected, genres_selected, years_selected):
    # Фильтрация данных по выбранным фильтрам
    filtered_df = df[
        (df['Platform'].isin(platforms_selected)) &
        (df['Genre'].isin(genres_selected)) &
        (df['Year_of_Release'] >= years_selected[0]) &
        (df['Year_of_Release'] <= years_selected[1])
    ]
    
    # Общее количество игр
    total_games = len(filtered_df)

    # Средняя оценка игроков
    avg_user_score = round(filtered_df['User_Score'].mean(), 1)

    # Средняя оценка критиков
    avg_critic_score = round(filtered_df['Critic_Score'].mean(), 1)

    # Средний возрастной рейтинг по жанрам
    avg_rating_by_genre_fig = create_avg_rating_by_genre_chart(filtered_df)
    
    scatter_fig = px.scatter(
        filtered_df, 
        x='Critic_Score', 
        y='User_Score', 
        color='Genre', 
        title='Оценки критиков и игроков по жанрам',
        labels={'Critic_Score': 'Оценки критиков', 'User_Score': 'Оценки игроков'}
    )
    
    scatter_fig.update_layout(
        xaxis_title='Оценки критиков',
        yaxis_title='Оценки игроков'
    )
    
    
    # Выпуск игр по годам и платформам
    stacked_area_df = filtered_df.groupby(['Year_of_Release', 'Platform']).size().reset_index(name='Game_Count')
    stacked_area_fig = px.area(
        stacked_area_df, 
        x='Year_of_Release', 
        y='Game_Count', 
        color='Platform', 
        title='Выпуск игр по годам и платформам',
        labels={'Year_of_Release': 'Год выпуска', 'Game_Count': 'Количество игр'}
    )

    stacked_area_fig.update_layout(
        xaxis_title='Год выпуска',
        yaxis_title='Количество игр'
    )
    
    
    return total_games, avg_user_score, avg_critic_score, avg_rating_by_genre_fig, scatter_fig, stacked_area_fig

if __name__ == '__main__':
    app.run_server(debug=True)

