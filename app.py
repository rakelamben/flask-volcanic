"""Studi kasus: Dashboard nilai mahasiswa dengan Flask + Chart.js.

Jalankan:
    pip install -r requirements.txt
    python app.py
lalu buka http://127.0.0.1:5000
"""
import pandas as pd
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
df = pd.read_csv("data/volcanic.csv")


def filter_data():
    data = df
    tahun = request.args.get("tahun")
    if tahun:
        data = data[data["date"].str[:4] == tahun]
    return data


@app.route("/")
def dashboard():
    tahun = sorted(df["date"].str[:4].unique().tolist())
    return render_template("dashboard.html", tahun=tahun)


@app.route("/api/ringkasan")
def ringkasan():
    data = filter_data()
    return jsonify(
        gunung=int(data["name"].nunique()),
        negara=int(data["country"].nunique()),
        total_erupsi=int(data["frequency"].sum()),
        catatan=int(len(data)),
    )


@app.route("/api/freq-gunung")
def freq_gunung():
    hasil = (
        filter_data()
        .groupby("name")["frequency"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    return jsonify(labels=hasil.index.tolist(), data=hasil.astype(int).tolist())


@app.route("/api/distribusi-negara")
def distribusi_negara():
    hasil = (
        filter_data()
        .groupby("country")["frequency"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    return jsonify(labels=hasil.index.tolist(), data=hasil.astype(int).tolist())


@app.route("/api/tren-dekade")
def tren_dekade():
    data = df.copy()
    data["tahun"] = pd.to_datetime(data["date"], errors="coerce").dt.year
    data = data.dropna(subset=["tahun"])
    data["dekade"] = (data["tahun"] // 10 * 10).astype(int)
    hasil = data.groupby("dekade")["frequency"].sum().sort_index()
    return jsonify(
        labels=[f"{dekade}–{dekade + 9}" for dekade in hasil.index],
        data=hasil.astype(int).tolist(),
    )


@app.route("/api/lokasi")
def lokasi():
    data = df.copy()
    titik = [
        {
            "x": float(row.longitude),
            "y": float(row.latitude),
            "name": row.name,
            "country": row.country,
            "frequency": int(row.frequency),
        }
        for row in data.itertuples(index=False)
    ]
    return jsonify(data=titik)



if __name__ == "__main__":
    app.run(debug=True)
