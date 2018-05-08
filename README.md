# Background

Bookscouter.com is a website which aids users in where to sell their used titles. However, there are many combinations of stores in which to sell a book along with different stores having different pricing algorithms for books.

This project contains a scraper for bookerscouter.com along with a linear programming algorithm to determine where to sell the books. The scraper takes ISBNs and runs them against bookscouter.com using Selenium. The output csv file is then used to determine which stores should receive which books for maximum profit.

Work is still being done on the linear programming section of the project to become more optimal, but, in the meantime, it should help users who want to get some help choosing to which stores they should sell their books.

Also, don't go crazy and input hundreds of books through the scraper. According to [Bookscouter's Terms of Use](https://bookscouter.com/terms) the site may be used for low-volume use. So be nice.