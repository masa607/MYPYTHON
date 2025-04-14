from flask import Flask, request, render_template
import matplotlib.pyplot as plt
import os
import math

app = Flask(__name__)

labels = ['外向性', '計画性', '柔軟性', '論理的思考', '直感的思考',
          'ストレス耐性', '独立性', '協調性', '創造性', '感受性']

def create_radar_chart(scores, filename='static/chart.png'):
    num_vars = len(labels)
    angles = [n / float(num_vars) * 2 * math.pi for n in range(num_vars)]
    scores += [scores[0]]
    angles += [angles[0]]

    plt.clf()
    fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
    ax.plot(angles, scores, marker='o')
    ax.fill(angles, scores, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    plt.savefig(filename, bbox_inches='tight')
    plt.close()

@app.route('/')
def index():
    return render_template('index.html', image_url='/static/chart.png')

@app.route('/update', methods=['POST'])
def update():
    try:
        data = request.json.get("row")
        scores = list(map(int, data[3:13]))
        create_radar_chart(scores)
        return {"status": "success", "url": "https://your-render-url.onrender.com/static/chart.png"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    app.run(debug=True)
