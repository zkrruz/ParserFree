import csv
from flask import Flask, render_template, request, redirect, send_file
from habrFree import print_data_as_dict, find_max_pages
from fl import print_data_as_dict_fl, find_max_pages_fl

app = Flask('ParserJobs')
db = {}

@app.route('/')
def home():
    return render_template('rep.html')

def export_to_csv(jobs, filename='parsed_jobs.csv'):
    with open(filename, mode='w', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Price', 'Link'])

        for job in jobs:
            title = job.get('title', '')
            price = job.get('price', job.get('salary', ''))
            link = job.get('link', '')
            writer.writerow([title, price, link])

@app.route('/report')
def report():
    global db
    keyword = request.args.get('keyword')
    if keyword is not None:
        keyword = keyword.lower()

        max_page_number = find_max_pages()
        max_pages_fl = find_max_pages_fl()

        if keyword not in db:
            habr_jobs = print_data_as_dict(max_page_number, keyword=keyword)
            fl_jobs = print_data_as_dict_fl(max_pages_fl, keyword=keyword)
            all_jobs = habr_jobs + fl_jobs
            db[keyword] = all_jobs
        else:
            all_jobs = db[keyword]

        export_csv = request.args.get('export_csv')

        if export_csv:
            export_to_csv(all_jobs)
            return send_file('parsed_jobs.csv', as_attachment=True)

        return render_template('rep.html', searchBy=keyword, jobs=all_jobs, habr_jobs=habr_jobs, fl_jobs=fl_jobs)
    else:
        return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)