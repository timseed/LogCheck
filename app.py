from flask import Flask
from LogReader import LogReader
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField


app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b743254'


class ReusableForm(Form):
    Exch = StringField('ExCh:', validators=[validators.required()])
    Feed = StringField('Feed:', validators=[validators.required()])

lr = LogReader()

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    global lr

    form = ReusableForm(request.form)
    data={}

    if request.method == 'POST':

        exch = request.form['Exch']
        feed = request.form['Feed']

        global lr
        good_data = lr.fake_data(start_date='1-Aug-2018',end_date='4-Aug-2018')
        df_fail = lr.Process(good_data,resample_freq='d')
        heat_map_picture = lr.Img(good_data,df_fail)

        if form.validate():
            # Save the comment here.
            data['heatmap'] = lr.plot_to_b64png(heat_map_picture)
            #flash('Ex: ' + exch + ' Fd: '+ feed)
        else:
            flash('All the form fields are required. ')
    return render_template('Log.html', form=form,data=data)




if __name__ == '__main__':
    app.run()
