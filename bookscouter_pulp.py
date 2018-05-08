import pandas as pd
import os
from pulp import LpProblem, lpSum, LpMaximize, LpVariable, LpSolverDefault, LpStatus, LpInteger, value

dat = pd.read_csv('bookscouter_results.csv')
dat_prices = dat[['ISBN', 'STORE', 'PRICE']]

# I sold this one already, so I needed to remove it from the dataset.
dat_prices = dat_prices[dat_prices.ISBN != '0674018214']


dat_pivot = dat_prices.pivot(index='ISBN', columns='STORE', values='PRICE').fillna(0).reset_index()


prob = LpProblem("The Bookscouter Problem", LpMaximize)

ISBN = dat_pivot.ISBN
Stores = dat_pivot.columns[1:]

dat_pivot.index = dat_pivot.ISBN
y = LpVariable.dicts('Stores', Stores, 0, None)

# Useful links that helped with this code:
	# http://benalexkeen.com/linear-programming-with-python-and-pulp-part-2/ 
	# https://www.redgamut.xyz/python-pulp-optimization-simple-logistics-example/
	# https://stackoverflow.com/questions/17772825/knapsack-in-pulp-adding-constraints-on-number-of-items-selected
	# https://www.linkedin.com/pulse/bin-packing-python-pulp-michael-basilyan/
	# https://cs.stackexchange.com/questions/12102/express-boolean-logic-operations-in-zero-one-integer-linear-programming-ilp
	# https://stackoverflow.com/questions/26886653/pandas-create-new-column-based-on-values-from-other-columns


prob += lpSum([y[store] for store in Stores]), 'Total_sum'

possible_ISBNinStore = [(isbn, store) for isbn in ISBN for store in Stores if dat_pivot.loc[isbn, store]>0]
z = LpVariable.dicts('itemInStore', possible_ISBNinStore, lowBound = 0, upBound = 1, cat = LpInteger)


# Contraints on the stores
prob += y['Bookstores.com'] >= 15.00
prob += y['Textbooks.com'] >= 10.00
prob += y['SellBackYourBook'] >= 7.50

#Powell's is really $9, but I got more money when I made this $10.

prob += y["Powell's"] >= 10.00


# Only allow for one book to be sold in one store.
for isbn in ISBN:
	prob += lpSum([z[(isbn, store)] for store in Stores if dat_pivot.loc[isbn, store]>0]) == 1


for store in Stores:
	prob += lpSum([z[(isbn, store)]*dat_pivot.loc[isbn, store] for isbn in ISBN if dat_pivot.loc[isbn, store]>0]) == y[store]

# The following is code to also try to count the number of "Powell's" variables since Powell's can 
# take a count of books (7) instead of just price. This didn't work.

# powell_count = {}
# powell_isbns=dat_pivot[dat_pivot["Powell's"] > 0].ISBN

# for isbn in powell_isbns:
# 	powell_count[isbn] = LpVariable("powell_"+isbn, 0, 1, cat='Binary')
# 	prob += z[(isbn, "Powell's")] <= 10000 * powell_count[isbn], "If Powell's_{0} is non-zero, then powellcount_{0} is forced to be 1".format(isbn)


# prob += lpSum([powell_count[isbn] for isbn in powell_isbns]) >= 7,"Ensuring at least 7 items are non-zero"

# This is the actual solver.
LpSolverDefault.msg = 1
prob.solve()

LpStatus[prob.status]


my_list = [(z[items[0]], value(z[items[0]])) for items in z.items() if value(z[items[0]]) > 0]

my_string = []
for books in my_list:
	string_to_append = books[0].name[14:-2].replace('_', ' ').split("', '")
	if len(string_to_append) == 1:
		string_to_append = string_to_append[0].split('\', "')
	my_string.append(string_to_append)

my_string_dict = [{isbn: store} for (isbn, store) in my_string]

result = {}
for d in my_string_dict:
	result.update(d)




def result_col(row):
	return result[row['ISBN']]


dat_prices['results'] = dat_prices.apply(result_col, axis=1)
dat2=dat_prices[dat_prices.results == dat_prices.STORE].sort_values('results')

total = []
for book_string in my_string:
	total.append((book_string[1], dat_pivot.loc[book_string[0], book_string[1]]))

#Now do some checking to see how much I make per store:
total_amount = pd.DataFrame(total, columns = ['STORE', 'TOTAL']).groupby('STORE').sum()

total_amount[total_amount > 5].sum()

#And also see how much I make for specific ISBNs
dat_prices[dat_prices.ISBN == '0684825503']

# Below is just a dictionary I have for reference for minimum prices for each store.
# You need to go to each site to see what its minimum is.

min_price = {'Bookstores.com': 15.00,
'Textbooks.com': 10.00,
'TextbookRush': 15.00,
'SellBackYourBook': 7.50}

