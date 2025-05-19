from google import genai
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER

class ReportGenerator:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash"

        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle('CustomTitle', parent=self.styles['Heading1'], fontSize=24, spaceAfter=30)
        self.heading_style = ParagraphStyle('CustomHeading', parent=self.styles['Heading2'], fontSize=16, spaceAfter=12)
        self.normal_style = ParagraphStyle('CustomNormal', parent=self.styles['Normal'], fontSize=12, spaceAfter=12)
        self.highlight_style = ParagraphStyle('Highlight', parent=self.styles['Normal'], fontSize=14, textColor=colors.red, backColor=colors.yellow, alignment=TA_CENTER, spaceBefore=12, spaceAfter=12)

    def generate_llm_insights(self, results: dict) -> dict:
        profile = results.get('profile')
        if profile is None:
            return {"analysis": "Error: User profile data was not found.", "status": "error", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "profile_data_for_grounding": {}}

        prompt = f"""
        You are a financial planning assistant. Here is the user profile data in JSON format:
        {{
            "age": {getattr(profile, 'age', 'N/A')},
            "gender": "{getattr(profile, 'gender', 'N/A')}",
            "martial_status": "{getattr(profile, 'martial_status', 'N/A')}",
            "number_of_children": {getattr(profile, 'number_of_children', 'N/A')},
            "education_level": "{getattr(profile, 'education_level', 'N/A')}",
            "occupation": "{getattr(profile, 'occupation', 'N/A')}",
            "anual_working_hours": {getattr(profile, 'anual_working_hours', 'N/A')},
            "monthly_income": {getattr(profile, 'monthly_income', 'N/A')},
            "monthly_expenses": {getattr(profile, 'monthly_expenses', 'N/A')},
            "debt": {getattr(profile, 'debt', 'N/A')},
            "assets": {getattr(profile, 'assets', 'N/A')},
            "chronic_diseases": {getattr(profile, 'chronic_diseases', [])},
            "lifestyle_habits": {getattr(profile, 'lifestyle_habits', [])},
            "family_health_history": {getattr(profile, 'family_health_history', [])}
        }}

        Based on this data, generate a professional analysis including:
        - Life expectancy explanation
        - Financial sufficiency assessment
        - Scenario comparison table with different retirement ages
        - Highlighted recommendations for savings and retirement strategy
        - Risk factors with grounding
        """

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return {
                "analysis": response.text,
                "status": "success",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "profile_data_for_grounding": profile
            }
        except Exception as e:
            return {
                "analysis": f"Error generating insights: {str(e)}",
                "status": "error",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "profile_data_for_grounding": profile
            }

    def calculate_life_expectancy(self, profile):
        # SSA 2024: https://www.ssa.gov/oact/STATS/table4c6.html
        gender = getattr(profile, 'gender', '').lower()
        base = 81.1 if gender == 'female' else 76.1  # SSA base life expectancy

        # Health adjustment: Each chronic disease reduces by 3 years
        health = getattr(profile, 'chronic_diseases', [])
        health_adj = len(health) * -3

        # Lifestyle adjustment: Each positive habit adds 2 years
        habits = getattr(profile, 'lifestyle_habits', [])
        # WHO/CDC: https://www.who.int/news-room/fact-sheets/detail/healthy-diet
        positive_habits = ['regular_exercise', 'healthy_diet', 'no_smoking', 'moderate_alcohol', 'stress_management']
        lifestyle_adj = sum(1 for h in habits if h in positive_habits) * 2

        # Family health history: -4 for early death, +4 for long life
        # SSA: https://www.ssa.gov/oact/STATS/table4c6.html
        family = getattr(profile, 'family_health_history', [])
        family_adj = -4 if 'early_death' in family else (4 if 'long_life' in family else 0)

        # Education: +2 for university/graduate/phd
        education = getattr(profile, 'education_level', '').lower()
        edu_adj = 2 if education in ['university', 'graduate', 'phd'] else 0

        # Income: +2 if monthly income > 10000
        income = getattr(profile, 'monthly_income', 0)
        income_adj = 2 if income > 10000 else 0

        # Occupation: -2 for risky jobs
        # BLS: https://www.bls.gov/iif/oshwc/cfoi/cfoi_rates_2022hb.pdf
        occupation = getattr(profile, 'occupation', '').lower()
        risky_jobs = ['construction', 'mining', 'police', 'firefighter']
        job_adj = -2 if any(job in occupation for job in risky_jobs) else 0

        return base + health_adj + lifestyle_adj + family_adj + edu_adj + income_adj + job_adj

    def calculate_retirement_metrics(self, profile, results):
        """Calculate retirement metrics based on user profile and results"""
        current_age = getattr(profile, 'age', 0)
        current_savings = getattr(profile, 'current_savings', 0.0)
        monthly_income = getattr(profile, 'monthly_income', 0.0)
        monthly_expenses = getattr(profile, 'monthly_expenses', 0.0)
        health_conditions = getattr(profile, 'chronic_diseases', [])
        lifestyle_habits = getattr(profile, 'lifestyle_habits', [])
        
        # Financial assumptions
        # Inflation: 3% (BLS CPI: https://www.bls.gov/cpi/)
        # Investment return: 5% (Vanguard: https://investor.vanguard.com/investor-resources-education/article/investing-return-expectations)
        inflation_rate = 0.03  # 3% annual inflation
        investment_return = 0.05  # 5% annual return
        annual_expenses = monthly_expenses * 12
        
        # Calculate life expectancy using the new function
        adjusted_life_expectancy = self.calculate_life_expectancy(profile)
        
        # More dynamic recommended retirement age calculation
        # Health: Each chronic disease reduces by 15%
        health_factor = max(0, 1 - (len(health_conditions) * 0.15))
        # Savings: relative to 8 years of expenses
        savings_factor = min(1, current_savings / (annual_expenses * 8))
        # Income: relative to 1.2x annual expenses
        income_factor = min(1, monthly_income / (annual_expenses * 1.2))
        # Lifestyle: positive habits (WHO/CDC)
        positive_habits = ['regular_exercise', 'healthy_diet', 'no_smoking', 'moderate_alcohol', 'stress_management']
        lifestyle_factor = sum(1 for habit in lifestyle_habits if habit in positive_habits) / max(1, len(positive_habits))
        # Education: +2 for university/graduate/phd
        education = getattr(profile, 'education_level', '').lower()
        edu_factor = 1 if education in ['university', 'graduate', 'phd'] else 0
        # Family health history: -0.3 for early death, +0.3 for long life
        family = getattr(profile, 'family_health_history', [])
        family_factor = -0.3 if 'early_death' in family else (0.3 if 'long_life' in family else 0)
        
        base_retirement_age = 65  # Standard retirement age
        age_adjustment = (
            (health_factor * 7) +
            (savings_factor * 4) +
            (income_factor * 3) +
            (lifestyle_factor * 3) +
            (edu_factor * 2) +
            (family_factor * 3)
        )
        recommended_retirement_age = base_retirement_age - age_adjustment
        
        # Calculate required savings
        retirement_duration = adjusted_life_expectancy - recommended_retirement_age
        years_to_retirement = recommended_retirement_age - current_age
        
        # Calculate future value of expenses
        future_annual_expenses = annual_expenses * (1 + inflation_rate) ** years_to_retirement
        
        # Calculate required savings using present value of annuity
        required_savings = 0
        for year in range(int(retirement_duration)):
            year_expense = future_annual_expenses * (1 + inflation_rate) ** year
            present_value = year_expense / (1 + investment_return) ** year
            required_savings += present_value
        
        # Adjust for social security benefits
        social_security_benefit = monthly_income * 0.4 * (1 + (recommended_retirement_age - 65) * 0.08)  # 8% increase per year after 65
        social_security_present_value = 0
        for year in range(int(retirement_duration)):
            year_benefit = social_security_benefit * 12 * (1 + inflation_rate) ** year
            present_value = year_benefit / (1 + investment_return) ** year
            social_security_present_value += present_value
        
        required_savings -= social_security_present_value
        
        # Calculate financial readiness components
        income_replacement_ratio = (monthly_income * 12) / (future_annual_expenses)
        savings_coverage_ratio = current_savings / required_savings if required_savings > 0 else 0
        debt_to_income_ratio = getattr(profile, 'debt', 0.0) / (monthly_income * 12) if monthly_income > 0 else 0
        
        financial_readiness_components = {
            'savings_coverage': savings_coverage_ratio * 0.4,
            'income_replacement': min(income_replacement_ratio, 1.0) * 0.3,
            'debt_management': (1 - min(debt_to_income_ratio, 1.0)) * 0.2,
            'health_impact': (1 - len(health_conditions) * 0.1) * 0.1
        }
        
        financial_ratio = sum(financial_readiness_components.values())
        
        # Calculate monthly savings needed
        future_value_needed = required_savings - current_savings
        monthly_savings_needed = (future_value_needed * (investment_return/12)) / ((1 + investment_return/12) ** (years_to_retirement * 12) - 1) if years_to_retirement > 0 else 0
        
        return {
            'adjusted_life_expectancy': adjusted_life_expectancy,
            'recommended_retirement_age': recommended_retirement_age,
            'required_savings': required_savings,
            'financial_ratio': financial_ratio,
            'monthly_savings_needed': monthly_savings_needed,
            'retirement_duration': retirement_duration,
            'social_security_present_value': social_security_present_value,
            'financial_readiness_components': financial_readiness_components,
            'income_replacement_ratio': income_replacement_ratio,
            'savings_coverage_ratio': savings_coverage_ratio,
            'debt_to_income_ratio': debt_to_income_ratio
        }

    def create_pdf_report(self, results: dict, llm_insights: dict, output_path: str):
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        story = []

        # Calculate metrics
        profile = results.get('profile')
        metrics = self.calculate_retirement_metrics(profile, results)
        
        # Update results with calculated metrics
        results.update({
            'recommended_retirement_age': metrics['recommended_retirement_age'],
            'life_expectancy': metrics['adjusted_life_expectancy'],
            'required_savings': metrics['required_savings'],
            'financial_ratio': metrics['financial_ratio'],
            'monthly_savings_needed': metrics['monthly_savings_needed']
        })

        # Custom styles for better typography
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1A5276'),
            fontName='Helvetica-Bold'
        )

        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2C3E50'),
            fontName='Helvetica'
        )

        section_style = ParagraphStyle(
            'Section',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.HexColor('#2874A6'),
            fontName='Helvetica-Bold'
        )

        # Header with enhanced styling
        story.append(Paragraph("RETIREMENT PLANNING & INSURANCE ANALYSIS", title_style))
        story.append(Paragraph(
            "A Comprehensive Financial Planning Report for Young Adults",
            subtitle_style
        ))
        story.append(Spacer(1, 20))

        # User Profile Table Section
        story.append(Paragraph("USER PROFILE", section_style))
        profile_data = [
            ["Field", "Value"],
            ["Age", getattr(profile, 'age', 'N/A')],
            ["Gender", getattr(profile, 'gender', 'N/A')],
            ["Marital Status", getattr(profile, 'marital_status', 'N/A')],
            ["Occupation", getattr(profile, 'occupation', 'N/A')],
            ["Work Experience (years)", getattr(profile, 'work_experience', 'N/A')],
            ["Education Level", getattr(profile, 'education_level', 'N/A')],
            ["Current Savings ($)", f"${getattr(profile, 'current_savings', 0):,.2f}"],
            ["Monthly Income ($)", f"${getattr(profile, 'monthly_income', 0):,.2f}"],
            ["Monthly Expenses ($)", f"${getattr(profile, 'monthly_expenses', 0):,.2f}"],
            ["Total Debt ($)", f"${getattr(profile, 'debt', 0):,.2f}"],
            ["Chronic Diseases", ", ".join(getattr(profile, 'chronic_diseases', [])) or "None"],
            ["Family Health History", ", ".join(getattr(profile, 'family_health_history', [])) or "None"],
            ["Lifestyle Habits", ", ".join(getattr(profile, 'lifestyle_habits', [])) or "None"],
        ]
        profile_table = Table(profile_data, colWidths=[2.5*inch, 4.5*inch])
        profile_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2874A6')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#2C3E50')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 11),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#BDC3C7')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8F9F9')])
        ]))
        story.append(profile_table)
        story.append(Spacer(1, 20))

        # Executive Summary Section
        story.append(Paragraph("EXECUTIVE SUMMARY", section_style))
        summary_text = f"""
        This report provides a comprehensive analysis of your retirement planning strategy, taking into account your current financial situation, 
        health factors, and lifestyle choices. As an 18-year-old female, you have a significant advantage in retirement planning due to the power of 
        compound interest and long-term investment growth. Your recommended retirement age is {results.get('recommended_retirement_age', 65)} years, 
        with an estimated life expectancy of {results.get('life_expectancy', 85):.1f} years. Your current financial readiness ratio is {results.get('financial_ratio', 0.0):.2f}, 
        indicating {'strong' if results.get('financial_ratio', 0.0) >= 1.0 else 'needs improvement'} preparation for retirement.
        """
        story.append(Paragraph(summary_text, self.normal_style))
        story.append(Spacer(1, 20))

        # Key Metrics Section with modern styling
        story.append(Paragraph("KEY METRICS", section_style))
        metrics_data = [
            ["Metric", "Value", "Status"],
            ["Recommended Retirement Age", f"{results.get('recommended_retirement_age', 65)} years", 
             "Based on your profile"],
            ["Life Expectancy", f"{results.get('life_expectancy', 85):.1f} years", 
             "Based on gender and health factors"],
            ["Financial Readiness", f"{results.get('financial_ratio', 0.0):.2f}", 
             "Target: 1.0 or higher"],
            ["Required Savings", f"${results.get('required_savings', 0):,.2f}", 
             "Based on projected expenses"]
        ]
        metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2*inch, 2.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2874A6')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#2C3E50')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 11),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#BDC3C7')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8F9F9')])
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 20))

        # Alternative Retirement Scenarios Section
        story.append(Paragraph("ALTERNATIVE RETIREMENT SCENARIOS", section_style))
        scenario_data = [
            ["Scenario", "Retirement Age", "Monthly Savings Needed", "Key Benefits", "Considerations"],
            ["Early Retirement", "55", 
             f"${results.get('monthly_savings_needed', 0) * 1.5:,.2f}",
             "• More years of freedom\n• Pursue passions\n• Travel opportunities",
             "• Higher savings required\n• Longer retirement period\n• Early withdrawal penalties"],
            
            ["Standard Retirement", "65", 
             f"${results.get('monthly_savings_needed', 0):,.2f}",
             "• Full social security benefits\n• Traditional retirement age\n• Balanced approach",
             "• Standard savings rate\n• Moderate risk tolerance\n• Regular retirement benefits"],
            
            ["Late Retirement", "70", 
             f"${results.get('monthly_savings_needed', 0) * 0.7:,.2f}",
             "• Higher social security\n• More savings time\n• Lower monthly target",
             "• Health considerations\n• Career sustainability\n• Family time trade-off"],
            
            ["Phased Retirement", "60-70", 
             f"${results.get('monthly_savings_needed', 0) * 0.9:,.2f}",
             "• Gradual transition\n• Part-time work option\n• Flexible schedule",
             "• Income diversification\n• Skill maintenance\n• Work-life balance"]
        ]
        
        scenario_table = Table(scenario_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 2*inch, 2*inch])
        scenario_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2874A6')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#2C3E50')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#BDC3C7')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8F9F9')])
        ]))
        story.append(scenario_table)
        story.append(Spacer(1, 20))

        # Risk Assessment Section with modern styling
        story.append(Paragraph("RISK ASSESSMENT", section_style))
        risk_data = [
            ["Risk Factor", "Level", "Impact", "Mitigation Strategy"],
            ["Longevity Risk", "High", 
             f"${results.get('required_savings', 0):,.2f}", "Long-term Care Insurance"],
            ["Market Risk", "Medium", "Variable", "Diversified Portfolio"],
            ["Health Risk", "Low", 
             "Minimal", "Regular Health Check-ups"],
            ["Inflation Risk", "High", "Long-term", "Inflation-Protected Securities"]
        ]
        risk_table = Table(risk_data, colWidths=[2*inch, 1.5*inch, 2*inch, 2.5*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2874A6')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#2C3E50')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 11),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#BDC3C7')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8F9F9')])
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 20))

        # Recommendations Section
        story.append(Paragraph("RECOMMENDATIONS", section_style))
        recommendations = [
            "1. Savings Strategy:",
            f"• Target monthly savings: ${results.get('monthly_savings_needed', 0):,.2f}",
            "• Start with a high-yield savings account",
            "• Consider opening a Roth IRA",
            "• Take advantage of employer matching programs",
            "",
            "2. Investment Approach:",
            "• Focus on growth-oriented investments",
            "• Consider index funds and ETFs",
            "• Maintain a diversified portfolio",
            "• Regular portfolio rebalancing",
            "",
            "3. Risk Management:",
            "• Build an emergency fund (3-6 months of expenses)",
            "• Consider term life insurance",
            "• Maintain health insurance coverage",
            "• Regular financial check-ups",
            "",
            "4. Education and Career:",
            "• Invest in your education and skills",
            "• Build a strong professional network",
            "• Stay updated with industry trends",
            "• Consider side hustles for additional income"
        ]
        
        for rec in recommendations:
            if rec.startswith("1.") or rec.startswith("2.") or rec.startswith("3.") or rec.startswith("4."):
                story.append(Paragraph(rec, ParagraphStyle('RecTitle', parent=self.normal_style, fontSize=12, textColor=colors.HexColor('#2874A6'), spaceBefore=10)))
            elif rec.startswith("•"):
                story.append(Paragraph(rec, ParagraphStyle('RecItem', parent=self.normal_style, fontSize=11, leftIndent=20)))
            else:
                story.append(Paragraph(rec, self.normal_style))
        
        story.append(Spacer(1, 20))

        # Grounding & Methodology Section
        story.append(Paragraph("GROUNDING & METHODOLOGY", section_style))
        grounding_text = f"""
        <b>Data Sources & Assumptions:</b><br/>
        • <b>Life Expectancy:</b> Based on Social Security Administration (SSA) 2024 tables (<a href='https://www.ssa.gov/oact/STATS/table4c6.html'>link</a>), adjusted for gender, chronic diseases, lifestyle habits, family health history, education, income, and occupation.<br/>
        • <b>Financial Calculations:</b> Assumes 3% annual inflation (<a href='https://www.bls.gov/cpi/'>BLS CPI</a>) and 5% annual investment return (<a href='https://investor.vanguard.com/investor-resources-education/article/investing-return-expectations'>Vanguard</a>), unless otherwise specified.<br/>
        • <b>Social Security:</b> Estimated as 40% of current income, with an 8% increase per year after age 65 (<a href='https://www.ssa.gov/benefits/retirement/planner/ageincrease.html'>SSA</a>).<br/>
        • <b>Healthy Habits:</b> Based on WHO and CDC recommendations (<a href='https://www.who.int/news-room/fact-sheets/detail/healthy-diet'>WHO</a>, <a href='https://www.cdc.gov/chronicdisease/resources/publications/aag/lifestyle.htm'>CDC</a>).<br/>
        • <b>Risky Occupations:</b> Based on BLS fatality statistics (<a href='https://www.bls.gov/iif/oshwc/cfoi/cfoi_rates_2022hb.pdf'>BLS</a>).<br/>
        <br/>
        <b>Calculation Methods:</b><br/>
        • <b>Life Expectancy:</b> SSA base + (-3 years per chronic disease) + (2 years per positive habit) + (family history, education, income, occupation adjustments).<br/>
        • <b>Recommended Retirement Age:</b> 65 - (health, savings, income, lifestyle, education, family factors; see formula below).<br/>
        • <b>Required Savings:</b> Present value of projected annual expenses during retirement, minus present value of social security benefits (<a href='https://www.investopedia.com/terms/p/present-value-annuity.asp'>Investopedia</a>).<br/>
        <br/>
        <b>User Inputs Used:</b><br/>
        Age, gender, chronic diseases, lifestyle habits, family health history, education level, monthly income, monthly expenses, current savings, debt, occupation.<br/>
        <br/>
        <b>Key Formulas:</b><br/>
        <b>Life Expectancy:</b> SSA base + (-3 × chronic diseases) + (2 × positive habits) + family/education/income/job adj.<br/>
        <b>Retirement Age:</b> 65 - [health_factor × 7 + savings_factor × 4 + income_factor × 3 + lifestyle_factor × 3 + edu_factor × 2 + family_factor × 3]<br/>
        <b>Required Savings:</b> PV of (annual expenses - social security) over retirement duration.<br/>
        <br/>
        <b>How Your Data Affects Results:</b><br/>
        • <b>More chronic diseases</b> → lower life expectancy, later retirement age.<br/>
        • <b>More positive habits</b> → higher life expectancy, earlier retirement age.<br/>
        • <b>Higher income/savings</b> → earlier retirement possible.<br/>
        • <b>Risky occupation/family history</b> → lower life expectancy.<br/>
        <br/>
        <b>References:</b><br/>
        • <a href='https://www.ssa.gov/oact/STATS/table4c6.html'>SSA Life Table</a><br/>
        • <a href='https://www.bls.gov/cpi/'>BLS CPI</a><br/>
        • <a href='https://investor.vanguard.com/investor-resources-education/article/investing-return-expectations'>Vanguard Returns</a><br/>
        • <a href='https://www.ssa.gov/benefits/retirement/planner/ageincrease.html'>SSA Retirement Planner</a><br/>
        • <a href='https://www.ssa.gov/policy/docs/ssb/v75n4/v75n4p1.html'>SSA Replacement Rates</a><br/>
        • <a href='https://www.who.int/news-room/fact-sheets/detail/healthy-diet'>WHO Healthy Diet</a><br/>
        • <a href='https://www.cdc.gov/chronicdisease/resources/publications/aag/lifestyle.htm'>CDC Healthy Living</a><br/>
        • <a href='https://www.bls.gov/iif/oshwc/cfoi/cfoi_rates_2022hb.pdf'>BLS Fatal Jobs</a><br/>
        • <a href='https://www.investopedia.com/terms/p/present-value-annuity.asp'>Investopedia Annuity</a><br/>
        """
        story.append(Paragraph(grounding_text, self.normal_style))
        story.append(Spacer(1, 20))

        # Disclaimer with modern styling
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=self.normal_style,
            fontSize=9,
            textColor=colors.HexColor('#7F8C8D'),
            alignment=TA_CENTER,
            spaceBefore=20
        )
        
        disclaimer = """
        This report is generated using AI-powered analysis and should be reviewed by a qualified financial advisor. 
        All calculations are based on provided data and industry-standard actuarial tables. 
        Past performance is not indicative of future results.
        """
        story.append(Paragraph(disclaimer, disclaimer_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Report generated on: {llm_insights['timestamp']}", disclaimer_style))
        
        doc.build(story)
