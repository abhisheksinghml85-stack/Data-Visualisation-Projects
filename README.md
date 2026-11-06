# India Census 2011 Explorer

A multi-page Streamlit dashboard for exploring district-level population, literacy, workforce, household, social, infrastructure, and geographic data from Census of India 2011.

The project includes dedicated pages for district exploration, literacy, rural/urban households,
state analysis and comparison, workforce, and household infrastructure.

## Run locally

```powershell
py -m pip install -r requirement.txt
py -m streamlit run app.py
```

## Deploy

The project is compatible with Streamlit Community Cloud and other Streamlit hosts.

1. Push the project to a Git repository.
2. Create a Streamlit app and select `app.py` as the entry point.
3. Use `requirement.txt` as the dependency file.
4. Keep both CSV files in the repository root.

The dashboard automatically resolves data files relative to the project directory, so it also works when the repository is opened from another working directory.
