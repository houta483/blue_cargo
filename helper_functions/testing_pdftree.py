import pdftotree

with open('./test.html', 'a+') as file:
    file.write(pdftotree.parse(
        "/Users/Tanner/code/products/glucose/original_data/CarliWilliams_01-15-2021.pdf", html_path=None, model_type=None, model_path=None, visualize=True))
