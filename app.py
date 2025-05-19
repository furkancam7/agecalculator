import gradio as gr
import os
from retirement_calculator import UserProfile, RetirementCalculator
from report_generator import ReportGenerator

# Initialize report generator with Gemini API key
GEMINI_API_KEY = "AIzaSyAhSQQh3oGf7J7w11W2WciLgxO6bLKGzbM"
report_generator = ReportGenerator(api_key=GEMINI_API_KEY)

def create_retirement_profile(
    age,
    gender,
    marital_status,
    occupation,
    work_experience,
    education_level,
    current_savings,
    monthly_income,
    monthly_expenses,
    debts,
    health_conditions,
    family_health_history,
    smoking,
    exercise,
    healthy_diet
):
    try:
        # Validate required inputs
        if not gender:
            return "Error: Please select a gender.", None
        if not marital_status:
            return "Error: Please select a marital status.", None
        if not education_level:
            return "Error: Please select an education level.", None
            
        # Convert inputs to appropriate types and handle None values
        age = int(age) if age is not None else 0
        work_experience = int(work_experience) if work_experience is not None else 0
        current_savings = float(current_savings) if current_savings is not None else 0.0
        monthly_income = float(monthly_income) if monthly_income is not None else 0.0
        monthly_expenses = float(monthly_expenses) if monthly_expenses is not None else 0.0
        debts = float(debts) if debts is not None else 0.0
        
        health_conditions_list = [condition.strip() for condition in health_conditions.split(",") if condition.strip()] if health_conditions else []
        family_health_history_list = [condition.strip() for condition in family_health_history.split(",") if condition.strip()] if family_health_history else []
        
        lifestyle_factors = {
            "smoking": bool(smoking),
            "regular_exercise": bool(exercise),
            "healthy_diet": bool(healthy_diet)
        }
        
        profile = UserProfile(
            age=age,
            gender=gender,
            marital_status=marital_status,
            occupation=occupation or "Not specified",
            work_experience=work_experience,
            education_level=education_level,
            current_savings=current_savings,
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            debts=debts,
            health_conditions=health_conditions_list,
            family_health_history=family_health_history_list,
            lifestyle_factors=lifestyle_factors
        )
        
        calculator = RetirementCalculator()
        results = calculator.recommend_retirement_age(profile)
        llm_insights = report_generator.generate_llm_insights(results)
        
        report_filename = f"retirement_report_{profile.age}_{profile.gender.lower()}.pdf"
        report_path = os.path.join("reports", report_filename)
        os.makedirs("reports", exist_ok=True)
        report_generator.create_pdf_report(results, llm_insights, report_path)
        
        output = f"""
        📊 Retirement Analysis Results:
        🎯 Recommended Retirement Age: {results['recommended_retirement_age']} years
        📈 Estimated Life Expectancy: {results['life_expectancy']:.1f} years
        💰 Financial Readiness Ratio: {results['financial_ratio']:.2f}
        📋 Scenario: {results['scenario'].title()}
        Financial Details:
        - Total Retirement Savings: ${results['financial_metrics']['total_retirement_savings']:,.2f}
        - Required Savings: ${results['financial_metrics']['required_savings']:,.2f}
        - Annual Retirement Expenses: ${results['financial_metrics']['annual_retirement_expenses']:,.2f}
        - Expected Retirement Duration: {results['financial_metrics']['retirement_duration']:.1f} years
        📝 AI-Powered Insights:
        {llm_insights['analysis']}
        📄 A detailed PDF report has been generated: {report_filename}
        """
        return output, report_path
    except Exception as e:
        return f"An error occurred: {str(e)}", None

demo = gr.Interface(
    fn=create_retirement_profile,
    inputs=[
        gr.Slider(minimum=18, maximum=100, step=1, label="Age"),
        gr.Radio(choices=["Male", "Female"], label="Gender"),
        gr.Radio(choices=["Single", "Married", "Divorced", "Widowed"], label="Marital Status"),
        gr.Textbox(label="Occupation"),
        gr.Slider(minimum=0, maximum=80, step=1, label="Years of Work Experience"),
        gr.Dropdown(
            choices=["High School", "Bachelor's", "Master's", "PhD", "Other"],
            label="Education Level"
        ),
        gr.Number(label="Current Savings ($)"),
        gr.Number(label="Monthly Income ($)"),
        gr.Number(label="Monthly Expenses ($)"),
        gr.Number(label="Total Debts ($)"),
        gr.Textbox(
            label="Health Conditions (comma-separated)",
            placeholder="e.g., diabetes, hypertension"
        ),
        gr.Textbox(
            label="Family Health History (comma-separated)",
            placeholder="e.g., heart disease, cancer"
        ),
        gr.Checkbox(label="Do you smoke?"),
        gr.Checkbox(label="Do you exercise regularly?"),
        gr.Checkbox(label="Do you maintain a healthy diet?")
    ],
    outputs=[
        gr.Textbox(label="Results", lines=15),
        gr.File(label="Download PDF Report")
    ],
    title="🎯 Retirement Age Calculator",
    description="Enter your information below to calculate your recommended retirement age.",
    theme=gr.themes.Soft()
)

if __name__ == "__main__":
    demo.launch(share=True) 