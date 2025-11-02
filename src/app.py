from flask import Flask, render_template

app = Flask(__name__, static_folder="static")

@app.get("/")
def home():
    return render_template("index.html")

def calculate_stop_duration(arrival_time, departure_time):
   
    return departure_time - arrival_time
if __name__ == "__main__":
    app.run(debug=True)
