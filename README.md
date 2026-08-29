# OLFYNZA

## Find Your Scent. Know Why It Fits.

OLFYNZA is an explainable perfume intelligence platform that helps users discover fragrances based on their scent preferences, intended occasion, environment and preferred fragrance strength.

Unlike a basic perfume recommender, OLFYNZA explains why each fragrance was selected, identifies matching scent evidence, checks notes the user prefers to avoid and provides transparent recommendation guidance.

## Live Application

[ttps://olfynza.streamlit.app

## GitHub Repository

[View the OLFYNZAm/adeeshachathurmina-ux/olfynza-perfume-intelligence

---

## Project Purpose

Choosing a perfume can be difficult because:

- Fragrance descriptions are often complex.
- Personal scent preferences are subjective.
- Users may not understand fragrance notes.
- Similar perfumes can be difficult to compare.
- Recommendations often do not explain why a perfume matches.
- Users may accidentally purchase fragrances that are very similar to perfumes they already own.

OLFYNZA addresses these challenges through a data-driven and explainable fragrance discovery experience.

---

## Main Features

### 1. Guided Scent Profile

Users complete a six-step scent profile covering:

- Preferred scent styles
- Main occasion
- Usage environment
- Preferred fragrance strength
- Budget preference
- Notes to avoid

The answers are stored during the current Streamlit session and used to build a perfume-related recommendation query.

### 2. Personalised Perfume Recommendations

OLFYNZA compares the user profile with a cleaned catalogue of 2,191 perfume records.

The platform returns the top fragrance matches using:

- TF-IDF text vectorisation
- Cosine similarity
- Fragrance-note similarity
- Description similarity
- Weighted recommendation ranking

### 3. Explainable Recommendations

Each recommendation includes:

- Perfume name and brand
- Ranking score
- Recommendation evidence level
- Directly matched preference terms
- Reasons behind the recommendation
- Selected-note conflict information
- Data-quality transparency
- Available fragrance notes

The ranking percentage represents text-matching evidence. It is not the probability that a user will like a perfume.

### 4. Recommendation Evidence Labels

OLFYNZA converts technical ranking evidence into understandable labels:

- Strong evidence
- Moderate evidence
- Limited evidence

These labels describe the amount of matching evidence available in the dataset. They are not scientifically validated preference probabilities.

### 5. Disliked-Note Checking

Users can select fragrance notes they prefer to avoid.

OLFYNZA checks the available note list of each recommended perfume and:

- Removes direct conflicts when enough alternatives exist
- Displays conflict warnings when relevant
- Avoids presenting the check as medical or allergy advice

### 6. Perfume Comparison

Users can compare two perfumes side by side.

The comparison includes:

- All available fragrance notes
- Directly shared notes
- Notes unique to each perfume
- Selected disliked-note conflicts
- Jaccard note similarity

Jaccard similarity is calculated as:

```text
Jaccard Similarity =
Number of Shared Notes
÷
Total Number of Unique Notes
×
100
```

The comparison percentage represents note-list overlap only. It does not measure perfume quality, performance or overall smell similarity.

### 7. Perfume Wardrobe Analyser

Users can select perfumes they currently own and analyse their collection.

The Wardrobe Analyser provides:

- Selected perfume count
- Unique fragrance-note count
- Most common notes
- Pairwise perfume similarity
- Highly similar perfume pairs
- Collection diversity indicator
- Note-data coverage
- Selected collection table

Perfume pairs with at least 40% direct note overlap are flagged for review.

A flagged pair does not prove that two perfumes smell identical. It only indicates substantial overlap between the available note lists.

### 8. Data Insights Dashboard

The Data Insights page provides transparent information about the cleaned dataset.

It includes:

- Total perfume records
- Unique brands
- Records containing fragrance notes
- Fragrance-note coverage
- Most represented brands
- Most common fragrance notes
- Searchable perfume catalogue
- Data-quality explanation

### 9. Anonymous Feedback System

Users can provide feedback for individual recommendations.

Available feedback options include:

- Helpful
- Not for me
- Too sweet
- Too strong
- Too light
- Too floral
- Too spicy
- Possible disliked-note conflict
- I would sample this

The feedback system:

- Uses an anonymous session ID
- Does not request a name
- Does not request an email address
- Does not request a phone number
- Limits comments to 500 characters
- Prevents the same feedback type from being submitted repeatedly for the same perfume in one session

The current stable portfolio release uses local CSV feedback storage. On Streamlit Community Cloud, locally stored feedback may not persist after an application reboot or redeployment.

### 10. Feedback Insights Dashboard

The Feedback Insights page can display:

- Total feedback records
- Reviewed perfume count
- Anonymous session count
- Helpful-response percentage
- Feedback type distribution
- Most reviewed perfumes
- Anonymous feedback record preview
- Privacy and interpretation notes

---

## How OLFYNZA Works

```text
User Opens OLFYNZA
        |
        v
Completes the Scent Profile
        |
        v
Profile Answers Are Mapped to Fragrance Terms
        |
        v
TF-IDF Converts Text into Numerical Features
        |
        v
Fragrance Notes and Descriptions Are Compared
        |
        v
Weighted Cosine Similarity Ranks Perfumes
        |
        v
Disliked-Note Preferences Are Checked
        |
        v
Explainable Top Matches Are Displayed
        |
        v
User Can Compare, Analyse or Give Feedback
```

---

## Recommendation Method

OLFYNZA creates separate TF-IDF representations for:

1. Fragrance notes
2. Perfume names, brands and descriptions

The current baseline ranking design is:

```text
Weighted Ranking Score =
70% Fragrance-Note Similarity
+
30% Description Similarity
+
Small Verified-Notes Adjustment
```

Fragrance notes receive greater weight because they provide more direct scent information than general product descriptions.

The 70% and 30% weights are documented project heuristics. They have not been scientifically validated and can be adjusted through future user evaluation.

---

## Profile-to-Query Mapping

Quiz answers are converted into perfume-related terms before recommendation.

Example:

```text
Selected Profile

Fresh
Citrus
University
Hot and humid
Moderate and balanced
```

May be mapped to terms such as:

```text
fresh clean bright citrus bergamot lemon orange grapefruit
light daytime aquatic moderate balanced smooth versatile
```

This improves matching because the dataset contains fragrance notes and descriptions rather than verified occasion or environmental labels.

The mappings are product-design heuristics, not scientific fragrance-suitability rules.

---

## Dataset Summary

| Dataset Measure | Value |
|---|---:|
| Original records | 2,191 |
| Final cleaned records | 2,191 |
| Unique brands | 249 |
| Records with fragrance notes | 2,111 |
| Records without fragrance notes | 80 |
| Fragrance-note coverage | 96.3% |
| Completely duplicated rows | 0 |
| Missing name records | 0 |
| Missing brand records | 0 |

### Dataset Fields

The original source contains:

- Name
- Brand
- Description
- Notes
- Image URL

The cleaning pipeline creates additional fields such as:

- `perfume_id`
- `has_notes`
- `has_description`
- `recommendation_eligible`
- `combined_text`

### Dataset Source

The project uses the Perfume Recommendation Dataset published by `nandini1999` on Kaggle.

https://www.kaggle.com/datasets/nandini1999/perfume-recommendation-dataset

The dataset page identifies the licence as CC0: Public Domain.

The raw dataset is kept separate from the processed deployment dataset so that the original source is not overwritten during data preparation.

---

## Data Preparation Pipeline

```text
Original CSV Dataset
        |
        v
Encoding Investigation
        |
        v
Data Audit
        |
        v
Column Validation
        |
        v
Text Cleaning
        |
        v
Whitespace Standardisation
        |
        v
Fragrance-Note Normalisation
        |
        v
Duplicate Validation
        |
        v
Stable Perfume ID Creation
        |
        v
Combined Text Feature Creation
        |
        v
Clean UTF-8 Dataset
```

### Data Cleaning Decisions

- The raw dataset is never overwritten.
- Missing perfume names and brands are treated as invalid identity records.
- Missing fragrance notes are kept as empty values.
- Marketing descriptions are not presented as verified fragrance notes.
- Exact duplicate records are checked.
- Duplicate name-and-brand combinations are checked.
- Repeated fragrance notes are removed while preserving order.
- The processed dataset is saved using UTF-8 encoding.
- Stable OLFYNZA perfume identifiers are generated.

### Generated Data Reports

The project includes:

```text
docs/data_audit_report.txt
docs/data_cleaning_report.txt
```

---

## Explainable AI Design

OLFYNZA was designed to avoid unexplained recommendations.

For every result, the platform can show:

- Which scent preferences matched
- Which fragrance terms were found
- How the selected occasion influenced the query
- How the selected environment influenced the query
- How the preferred strength influenced the query
- Whether a disliked note was detected
- Whether verified note data is available
- How much matching evidence supports the result

The explanation reflects the available dataset information and documented heuristic mappings.

OLFYNZA does not claim that its recommendations are scientifically guaranteed.

---

## Collection Diversity Method

The Wardrobe Analyser calculates every possible perfume pair in the selected collection.

The current collection diversity indicator is:

```text
Collection Diversity Score =
100
-
Average Pairwise Note Similarity
```

Interpretation labels include:

- Highly varied
- Balanced variety
- Moderately similar
- Highly similar
- Not enough perfumes
- Insufficient note data

This is a transparent project heuristic rather than a scientific measurement of fragrance diversity.

---

## Automated Testing

OLFYNZA currently includes **62 passing automated tests**.

Run all tests using:

```bash
python -m pytest tests -v
```

The test suite covers:

### Dataset Tests

- Dataset availability
- Dataset loading
- Required columns
- Non-empty catalogue
- Unique perfume identifiers
- Product-name completeness
- Brand completeness

### Recommendation Tests

- Recommendation result count
- Required result fields
- Descending score order
- Empty-query rejection
- Positive ranking scores

### Explainability Tests

- Explanation structure
- Disliked-note conflict detection
- Missing-note transparency

### Confidence Tests

- Strong-evidence behaviour
- Limited-evidence behaviour
- User guidance availability

### Perfume Comparison Tests

- Note cleaning
- Duplicate-note removal
- Missing-note handling
- Jaccard similarity
- Shared notes
- Unique notes
- Conflict detection
- Complete comparison output

### Wardrobe Analyser Tests

- Perfume record validation
- Collection note extraction
- Note frequency calculation
- Pairwise comparison count
- Most similar pair detection
- Possible duplicate detection
- Diversity-score boundaries
- Single-perfume handling
- Note-data coverage
- Complete wardrobe analysis
- Empty wardrobe handling

### Feedback Tests

- Feedback text cleaning
- Maximum comment length
- Anonymous feedback ID format
- Anonymous session ID format
- Supported feedback options
- Input validation
- Feedback record structure
- Absence of identity fields
- Local CSV creation
- Feedback saving
- Duplicate prevention
- Feedback summary calculation

---

## Technology Stack

### Programming and Data Science

- Python
- Pandas
- NumPy
- Scikit-learn

### Machine Learning and Similarity

- TF-IDF Vectorisation
- Cosine Similarity
- Jaccard Similarity
- Rule-based Profile Mapping
- Evidence-based Explanations

### Application and Visualisation

- Streamlit
- Plotly
- HTML and CSS styling

### Testing and Engineering

- Pytest
- Modular Python structure
- Virtual environments
- Git
- GitHub
- Streamlit Community Cloud

---

## Project Structure

```text
OLFYNZA/
|
|-- app.py
|
|-- pages/
|   |-- 1_Scent_Profile.py
|   |-- 2_Recommendations.py
|   |-- 3_Data_Insights.py
|   |-- 4_Perfume_Comparison.py
|   |-- 5_My_Wardrobe.py
|   `-- 6_Feedback_Insights.py
|
|-- src/
|   |-- data/
|   |   |-- data_audit.py
|   |   |-- clean_data.py
|   |   |-- data_loader.py
|   |   `-- supabase_feedback.py
|   |
|   |-- explainability/
|   |   `-- explanation.py
|   |
|   |-- features/
|   |   |-- profile_mapper.py
|   |   |-- perfume_comparison.py
|   |   |-- wardrobe_analyser.py
|   |   `-- feedback_manager.py
|   |
|   `-- models/
|       |-- recommender.py
|       `-- confidence.py
|
|-- data/
|   |-- raw/
|   |-- processed/
|   `-- feedback/
|
|-- tests/
|   |-- test_confidence.py
|   |-- test_data_loader.py
|   |-- test_explanation.py
|   |-- test_feedback_manager.py
|   |-- test_perfume_comparison.py
|   |-- test_recommender.py
|   `-- test_wardrobe_analyser.py
|
|-- docs/
|   |-- data_audit_report.txt
|   `-- data_cleaning_report.txt
|
|-- assets/
|-- requirements.txt
|-- .gitignore
`-- README.md
```

---

## Local Installation

### 1. Clone the Repository

Copy the repository URL from the GitHub repository page and run:

```bash
git clone <repository-url>
```

### 2. Enter the Project Directory

```bash
cd olfynza-perfume-intelligence
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate on Windows PowerShell

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Run the Application

```bash
python -m streamlit run app.py
```

The local application will normally be available at:

```text
http://localhost:8501
```

---

## Rebuilding the Dataset Locally

If the processed dataset is unavailable:

1. Download the source dataset from Kaggle.
2. Place the original file at:

```text
data/raw/final_perfume_data.csv
```

3. Run the data audit:

```bash
python src/data/data_audit.py
```

4. Run the cleaning pipeline:

```bash
python src/data/clean_data.py
```

5. Confirm that this file was created:

```text
data/processed/perfumes_clean.csv
```

---

## Current Limitations

- Fragrance preferences remain subjective.
- Similarity does not guarantee that a user will like a perfume.
- The dataset does not provide verified market prices.
- Budget preference is displayed but is not used as a verified price filter.
- The dataset does not contain verified occasion labels.
- The dataset does not contain verified climate-suitability labels.
- The dataset does not contain verified fragrance-performance labels.
- Environment, occasion and strength mappings are documented heuristics.
- Some records do not contain verified fragrance-note lists.
- Note comparisons do not consider note concentration or development over time.
- Jaccard similarity treats available notes equally.
- The current live feedback feature uses temporary local application storage.
- Live feedback may not persist after a cloud reboot or redeployment.
- OLFYNZA does not provide medical, allergy or skin-safety advice.
- Users should test a fragrance sample before purchasing when possible.

---

## Responsible Design Principles

OLFYNZA follows these principles:

- Explain recommendations rather than showing unexplained results.
- Distinguish text similarity from user-preference probability.
- Disclose missing fragrance-note information.
- Avoid presenting descriptions as verified fragrance notes.
- Clearly label heuristic rules.
- Avoid guaranteeing product performance.
- Avoid making medical or allergy claims.
- Collect feedback without requesting direct personal identity information.
- Encourage sampling before a full-bottle purchase.

---

## Future Improvements

- Permanent cloud feedback storage
- Real user evaluation
- Recommendation weight optimisation
- User-controlled recommendation diversity
- Fragrance-family classification
- Price and bottle-size dataset enrichment
- Sri Lankan market availability
- Cost-per-wear estimation
- Affordable alternative discovery
- User accounts and saved wardrobes
- Persistent scent profiles
- Fragrance concentration analysis
- Seasonal recommendation controls
- Recommendation history
- Improved mobile navigation
- Sinhala language support
- Additional accessibility testing

---

## Author

**Adeesha Chathurmina**

Data Science undergraduate interested in:

- Machine learning
- Recommendation systems
- Explainable AI
- Data visualisation
- Responsible data products
- Practical user-centred applications

---

## Disclaimer

OLFYNZA is an educational and portfolio Data Science project.

Fragrance preference is subjective. Recommendations are generated from available text and fragrance-note information and should be treated as decision-support suggestions only.

OLFYNZA does not provide medical, allergy, dermatological, safety or guaranteed purchasing advice.