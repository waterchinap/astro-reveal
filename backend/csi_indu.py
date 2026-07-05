import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import polars as pl

    return (pl,)


@app.cell
def _(pl):
    df = pl.read_excel('indu.xlsx')
    return (df,)


@app.cell
def _(df):
    df
    return


@app.cell
def _(df):
    df.columns = [
    "code",
    "name",
    "中证一级行业分类代码",
    "cat1",
    "中证二级行业分类代码",
    "cat2",
    "中证三级行业分类代码",
    "cat3",
    "中证四级行业分类代码",
    "cat4"
    ]
    return


@app.cell
def _(df, pl):
    df.group_by(pl.col('cat1')).agg(pl.len()).sort(by='len',descending=True)
    return


@app.cell
def _(df, pl):
    df.with_columns(pl.col('code').str.contains('HK').alias('HK')).group_by('HK').agg(pl.len())
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
