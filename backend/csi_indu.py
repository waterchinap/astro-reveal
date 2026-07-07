import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import polars as pl

    return (pl,)


@app.cell
def _(pl):
    df = pl.read_excel('399317.xlsx')
    return (df,)


@app.cell
def _(df):
    df
    return


@app.cell
def _(df):
    df.columns = [
      "日期",
      "code",
      "name",
      "indu",
      "mv",
      "wt"
    ]
    return


@app.cell
def _(df, pl):
    dft = df.with_columns(pl.col('mv', 'wt').cast(pl.Float32))
    return (dft,)


@app.cell
def _(dft, pl):
    dft.group_by(pl.col('indu')).agg([
        pl.sum('mv'),
        pl.count('code').alias('count'),
        (pl.sum("mv") / pl.count("code")).alias("mv_per_count")
    ]).sort('mv', descending=True)
    return


@app.cell
def _(dft):
    dft.sort('mv', descending=True).group_by('indu', maintain_order=True).head(5)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
