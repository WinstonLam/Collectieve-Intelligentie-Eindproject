from data import CITIES, BUSINESSES, USERS, REVIEWS, TIPS, CHECKINS
import pandas as pd
import numpy as np
import random
import data


def extract_categories(df, businesses):
    """Create an unfolded genre dataframe. Unpacks genres seprated by a '|' into seperate rows.

    Arguments:
    movies -- a dataFrame containing at least the columns 'movieId' and 'genres' 
              where genres are seprated by '|'
    """
    
    categories = businesses.apply(lambda row: pd.Series([row['business_id']] + row['categories'].lower().split(", ")), axis=1)
    stack_genres = categories.set_index(0).stack()
    df_stack_genres = stack_genres.to_frame()
    df_stack_genres['business_id'] = stack_genres.index.droplevel(1)
    df_stack_genres.columns = ['categories', 'business_id']
    return df_stack_genres.reset_index()[['business_id', 'categories']]


def pivot_genres(df):
    """Create a one-hot encoded matrix for genres.
    
    Arguments:
    df -- a dataFrame containing at least the columns 'movieId' and 'genre'
    
    Output:
    a matrix containing '0' or '1' in each cell.
    1: the movie has the genre
    0: the movie does not have the genre
    """
    #categories = set(list(extract_categories(df)['categories']))
    return df.pivot_table(index = 'business_id', columns = 'categories', aggfunc = 'size', fill_value=0)


def create_similarity_matrix_categories(matrix):
    """Create a  """
    npu = matrix.values
    m1 = npu @ npu.T
    diag = np.diag(m1)
    m2 = m1 / diag
    m3 = np.minimum(m2, m2.T)
    return pd.DataFrame(m3, index = matrix.index, columns = matrix.index)


def select_neighborhood(similarity_matrix, utility_matrix, target_business):
    # list of businesses that are related to the target_business
    similar = list(similarity_matrix[similarity_matrix[target_business] > 0].index)
    # businesses that are related 
    rest = list(similar)
    
    return similarity_matrix[target_business][rest] 


def recommend(user_id=None, business_id=None, city=None, n=10):
    """
    Returns n recommendations as a list of dicts.
    Optionally takes in a user_id, business_id and/or city.
    A recommendation is a dictionary in the form of:
        {
            business_id:str
            stars:str
            name:str
            city:str
            adress:str
        }
    """



    # initialize
    rand = []
    Datalijst_Home = []
    Datalijst_Business = []
    rand_bus = []



    """ Als er geen stad wordt meegegeven, wordt er een random stad gekozen."""
    if not city:
        city = random.choice(CITIES)
    

    """ Recommender code voor wanneer er geen business wordt meegegeven. Dit gebeurt op de hoofdpagina."""
    if not business_id:

        # selecteer de beste zaken op basis van de random gekozen stad
        businesses = pd.DataFrame(data.BUSINESSES[city])
        # de zaken moet minstens 20 ratings hebben en ze zijn geordend op beste gemiddelde sterren
        the_best = businesses[businesses['review_count'] >20].sort_values('stars',ascending = False)[:6]

        best_list = list(the_best['business_id'])

        # voor de sliders laten we 4 random gekozen business zien op de homepage
        while len(rand) < 4:
            zaak = random.choice(BUSINESSES[city])['business_id']
            if zaak not in best_list:
                rand.append(zaak) 
            set(rand)
    
        home = rand + best_list

        # loop door de lijst en selecteer de business
        for i in home:
    
            # zoek de juiste data van de business op
            for j in BUSINESSES[city]:
                if j['business_id'] == i:
            
                    # zet de data in een lijst die werkt met de HTML output
                    Datalijst_Home.append(j)

        # return de lijst met aanbevolen businesses
        return Datalijst_Home


    """ Recommender code voor wanneer er wel een business wordt meegegeven. Dit gebeurt op de businesspagina."""
    if business_id:

        # selecteer de beste zaken op basis van de random gekozen stad
        businesses = pd.DataFrame(data.BUSINESSES[city])

        # maak een dataframe van de businesses van de meegegeven stad
        df = pd.DataFrame(data.BUSINESSES[city])

        # maak een utility matrix
        df_matrix = pivot_genres(extract_categories(df, businesses))

        # maak een similariteits matrix gebaseerd op categorieën 
        df_similarity = create_similarity_matrix_categories(df_matrix)

        # bereken de neighborhood
        neighborhood = select_neighborhood(df_similarity, df_matrix, business_id)
        rec_bus = neighborhood.sort_values(ascending = False)

        # selecteer de beste zaken op basis van de random gekozen stad
        businesses = pd.DataFrame(data.BUSINESSES[city])
        
        # de zaken moet minstens 20 ratings hebben en ze zijn geordend op beste gemiddelde sterren
        best_bus = list(rec_bus[1:7].index)

        # voor de sliders laten we 4 random gekozen business zien op de businesspage
        while len(rand_bus) < 4:
            zaak = random.choice(BUSINESSES[city])['business_id']
            if zaak not in best_bus:
                rand_bus.append(zaak) 
            set(rand_bus)

        # maak van de business_id's een lijst
        bus_page = best_bus + rand_bus

        # loop door de lijst en selecteer de business
        for i in bus_page:
    
            # zoek de juiste data van de business op
            for j in BUSINESSES[city]:
                if j['business_id'] == i:
            
                    # zet de data in een lijst die werkt met de HTML output
                    Datalijst_Business.append(j)

        # return de lijst met aanbevolen businesses
        return Datalijst_Business







    