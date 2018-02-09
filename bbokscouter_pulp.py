import pandas as pd
import os
from pulp import *

os.chdir('/Users/zucks/Documents/bookscouter/')
dat = pd.read_csv('/Users/zucks/Documents/bookscouter/bookscouter_dat.csv')

dat_pivot = dat.pivot(index='ISBN', columns='Store', values='Price').fillna(0).reset_index()

# dat_pivot['powellcount'] = 1

prob = LpProblem("The Bookscouter Problem", LpMaximize)

ISBN = dat_pivot.ISBN
Stores = dat_pivot.columns[1:]



dat_pivot.index = dat_pivot.ISBN
# x = LpVariable.dicts('ISBNS', ISBN, LpInteger, cat='Binary')
y = LpVariable.dicts('Stores', Stores, 0, None)

# http://benalexkeen.com/linear-programming-with-python-and-pulp-part-2/ 
# https://www.redgamut.xyz/python-pulp-optimization-simple-logistics-example/

	# x[isbn].bounds(MinVols[isbn], MaxVols[isbn])
	''' SET THE OBJECTIVE FUNCTION '''
	''' SET THE OBJECTIVE FUNCTION '''


# for store in Stores:
# 	prob += sum(dat_pivot.loc[isbn,store]*x[isbn] for isbn in ISBN) <= y[store]

prob += lpSum([y[store] for store in Stores]), 'Total_sum'

possible_ISBNinStore = [(isbn, store) for isbn in ISBN for store in Stores if dat_pivot.loc[isbn, store]>0]
z = LpVariable.dicts('itemInStore', possible_ISBNinStore, lowBound = 0, upBound = 1, cat = LpInteger)


prob += y['Bookstores.com'] >= 15.00
prob += y['SellBackYourBook'] >= 7.50
# prob += y['powellcount'] >= 7.00


# y_b=[]

# for index in range(25):
#     y_b[index] = LpVariable("y_b"+str(index), 0, 1) #binary variables
#     prob += x[index] <= 10000 * y_b[index], "If x%s is non-zero, then y_b%s is forced to be 1",%index, %index

# prob += lpSum([y_b[i] for i in range(25)]) >= 10,"Ensuring at least 10 items are non-zero"





# https://stackoverflow.com/questions/17772825/knapsack-in-pulp-adding-constraints-on-number-of-items-selected


for isbn in ISBN:
	prob += lpSum([z[(isbn, store)] for store in Stores if dat_pivot.loc[isbn, store]>0]) == 1


for store in Stores:
	prob += lpSum([z[(isbn, store)]*dat_pivot.loc[isbn, store] for isbn in ISBN if dat_pivot.loc[isbn, store]>0]) == y[store]


powell_count = {}
powell_isbns=dat_pivot[dat_pivot["Powell's"] > 0].ISBN

for isbn in powell_isbns:
	powell_count[isbn] = LpVariable("powell_"+isbn, 0, 1, cat='Binary')
	prob += z[(isbn, "Powell's")] <= 10000 * powell_count[isbn], "If Powell's_{0} is non-zero, then powellcount_{0} is forced to be 1".format(isbn)


prob += lpSum([powell_count[isbn] for isbn in powell_isbns]) >= 7,"Ensuring at least 7 items are non-zero"


# for isbn in ISBN:
# 	for store in Stores:
# 		if dat_pivot.loc[isbn, store]>0:
# 			prob += lpSum([x[isbn]]) == y[store]


# for store in Stores:
# 	if dat_pivot.loc[isbn, store]>0:
# 			prob += lpSum([x[isbn] for isbn in ISBN]) == y[store]


LpSolverDefault.msg = 1
prob.solve()

LpStatus[prob.status]

possible_ItemInBin = [(itemTuple[0], binNum) for itemTuple in items for binNum in range(maxBins)]
# https://www.linkedin.com/pulse/bin-packing-python-pulp-michael-basilyan/


# https://cs.stackexchange.com/questions/12102/express-boolean-logic-operations-in-zero-one-integer-linear-programming-ilp
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

dat['result'] = dat.isbn

# https://stackoverflow.com/questions/26886653/pandas-create-new-column-based-on-values-from-other-columns


def result_col(row):
	return result[row['ISBN']]


dat['results'] = dat.apply(result_col, axis=1)
dat2=dat[dat.results == dat.Store]

total = []
for book_string in my_string:
	total.append((book_string[1], dat_pivot.loc[book_string[0], book_string[1]]))

pd.DataFrame(total, columns = ['STORE', 'TOTAL']).groupby('STORE').sum()





powell_count

min_price = {'Bookstores.com': 15.00,
'Textbooks.com': 10.00,
'TextbookRush': 15.00,
'SellBackYourBook': 7.50}

