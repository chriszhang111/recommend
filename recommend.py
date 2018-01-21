'''
Movie Recommend System version 0.1
Author:Ruizhe Zhang 12/2017
'''
import imp
from imp import reload
import texttable
import sys
from texttable import Texttable
from collections import defaultdict
import math
import scipy.spatial.distance as ssd
from heapq import*
from functools import wraps

filepath = '/Users/chris/Desktop/ml-100k/'


"""

"""
'''

tb = Texttable()
tb.set_deco(Texttable.HEADER | Texttable.VLINES | Texttable.HLINES | Texttable.BORDER)
tb.add_rows([
    ['Name','Age'],
    ['TM','80'],
    ['AB','12']
])
'''
class Movie_Recommand(object):

    def __init__(self):
        self.user_rating = {}
        self.user_aver_rating = {}
        self.movie_user = defaultdict(set)
        self.movie_list = {}
        self.movie_to_id = {}

    def readfile(self,filename):
        contents = []
        f = open(filename,"r",encoding="ISO-8859-1")
        contents = f.readlines()
        f.close()
        return contents



    def Read_file_requried(self,func):

        def wrapper(self,*kw,**args):
            if not self.movie_list and not self.user_rating:
                raise ('Need read files first')
            return func(*kw,**args)




        return wrapper



    def getMovieList(self,filename):
        """

        :param filename:
        :return: dict ->{Movie.id:[info...]}
        """
        contents = self.readfile(filepath+filename)
        Movie_info = {}

        for content in contents:
            single_info = content.split('|')
            Movie_info[single_info[0]] = single_info[1]
            self.movie_to_id[single_info[1]] = single_info[0]

        self.movie_list = Movie_info

        return Movie_info


    def getRatingInfo(self,datafile):
        """

        :param datafile: the u.data file to extract 3 dictionary including:
                user-movie rating table
                user's average rating table
                movie-user table
        :return:
        """
        user_rating = {}               ###users rating on every movie
        user_aver_rating = {}        ###users average rating
        movie_user = defaultdict(set)
        contents = self.readfile(filepath+datafile)
        for single_item in contents:
            single_item = single_item.split('\t')
            if single_item[0] not in user_rating:
                user_rating[single_item[0]] = {}
            user_rating[single_item[0]][single_item[1]] = int(single_item[2])

            movie_user[single_item[1]].add(single_item[0])
        for user,table in user_rating.items():
            total = 0

            for movie,rating in table.items():
                total += rating

            user_aver_rating[user] = total / len(user_rating[user])
        self.user_rating = user_rating
        self.user_aver_rating = user_aver_rating
        self.movie_user = movie_user
        return user_rating,user_aver_rating,movie_user





    def calSimilarity(self,user_rating,user1,user2,args = 5):
        """
        the calculation of Similarity
        Fomula: 1−u⋅v/(||u||2 * ||v||2)

        :param user_rating: dict{dict}  -> {'user1:{movie1:1,movie2:2}','user2:{movie3:...}',...}
        :param user1: str
        :param user2: str
        :param args:
        :return:  similarlty:float
        """
        rating1,rating2 = [],[]
        user1 = user_rating[user1]
        user2 = user_rating[user2]

        for i in user1.keys() & user2.keys():
            rating1.append(user1[i])
            rating2.append(user2[i])
        if len(rating1) < args:
            return 0.001
        return 1-ssd.cosine(rating1,rating2)


    def theKNearNeibor(self,user_rating,movie_user,user,k = 10):
        """
        Select k nearest neighbors based on the similarity

        :param user_rating: dict{dict}  -> {'user1:{movie1:1,movie2:2}','user2:{movie3:...}',...}
        :param movie_user: defalutdict(set) -> {movie1:(user1,user2,user3...),movie2:(user4...),...}
        :param user: str
        :param k: int
        :return: list of neighbors:list
        """
        neighbors = set()
        user_list = user_rating[user]   #{movie1:rate,movie2:rate,...}
        list = []

        for movie in user_list.keys():
            for neighbor in movie_user[movie]:
                if neighbor != user and neighbor not in neighbors:
                    neighbors.add(neighbor)
        for nei in neighbors:
            similarity = self.calSimilarity(user_rating,user,nei)
            list.append([similarity,nei])
        list.sort(key=lambda x:x[0],reverse=True)
        return list[:k]

    def predictOnMovie(self,user,movie,neibor_list,user_rating,user_aver_rating):
        """
        The predict rating on a movie that the user has not seen
        Fomula: R(user,movie) = Rate_movie(user)+ sum(similarity(user,neibor)*(R(neibor,movie)*Rate_movie(user))/sum(similarity(user,neibor))
        :param user: str -> user.id
        :param movie: str -> movie.id
        :param neibor_list: List -> [ [sim1,nei1],[sim2,nei2] ...]  x[0]:similarlty of user and neighbor x[1]:neighbor
        :param user_rating:
        :param user_aver_rating:
        :return:
        """
        predict = user_aver_rating[user]
        numerator, denominator = 0.0,0.0
        for sim, neighbor in neibor_list:
            if movie in user_rating[neighbor]:
                numerator += sim*(user_rating[neighbor][movie]-user_aver_rating[neighbor])
                denominator += sim
        predict += numerator/denominator
        return predict


    def userBasedCF(self,movie_list,user_rating,user_aver_rating,movie_user,user,k = 20):
        Recommend_List = []
        Used = set()
        neighbor_list = self.theKNearNeibor(user_rating,movie_user,user)

        for sim,nei in neighbor_list:
            for movie,rating in user_rating[nei].items():
                if movie not in user_rating[user] and movie not in Used:
                    pred = self.predictOnMovie(user,movie,neighbor_list,user_rating,user_aver_rating)

                    if pred > user_aver_rating[user]:
                        Recommend_List.append((movie,round(pred,2)))
                        Used.add(movie)
        Recommend_List.sort(key=lambda x:x[1],reverse=True)
        return Recommend_List[:15]




















a = Movie_Recommand()
a.getMovieList('u.item')
j = 0
for i ,v in a.movie_to_id.items():
    if j == 10:
        break

    print(i,v)
    j +=1

##b,c,d = a.getRatingInfo('u.data')
##e = a.getMovieList('u.item')

##recomMovies = a.userBasedCF(e,b,c,d,'50')

'''
table = Texttable()
table.set_deco(Texttable.HEADER)
table.set_cols_dtype(['t',  # text
                      't'])  # float (decimal)
table.set_cols_align(["l", "l"])
rows = []
rows.append([u"recommended movie", u"predicted rating"])
for mid, pred in recomMovies:
    rows.append([e[mid], pred])
table.add_rows(rows)
print(table.draw())

'''




























