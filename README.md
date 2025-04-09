# AdNova

## Overview

AdNova leverages advanced LLM models (primarily GPT-4) to generate compelling marketing content based on detailed campaign briefs and audience analysis. This system implements autonomous agent principles including:

1. **Planning**: Breaking down complex ad creation tasks into manageable steps with goal decomposition.
2. **Memory**: Storing campaign information, ad content, and feedback for continuous learning.
3. **Reflection**: Learning from feedback to improve future ad generations.
4. **Tool Use**: Specialized tools for audience analysis, brand voice creation, and content generation.

The system is designed to help marketers streamline their ad creation process and produce higher quality marketing content by leveraging the power of modern language models.

## Features

- **Campaign Brief Creation**: Define campaign parameters including product details, target audience, goals, tone, and more.
- **Audience Analysis**: Automatic extraction of demographic and psychographic insights from target audience descriptions.
- **Multi-Format Ad Generation**: Generate diverse marketing content including:
  - Social media posts
  - Headlines/titles
  - Email subject lines
  - Banner ad copy
  - Product descriptions
  - Landing page content
  - Video/radio scripts
  - Press releases
  - Blog posts
- **Feedback Processing**: Analyze client feedback to extract actionable insights for improvement.
- **Self-Improvement**: Learn from feedback to continuously improve ad quality over time.
- **Brand Voice Management**: Create and maintain consistent brand voice across all marketing content.
- **Campaign Recommendations**: Get AI-powered recommendations for campaign strategy.
- **Analytics & Insights**: View performance metrics and audience insights.
- **Export Capabilities**: Export all campaign assets in various formats (JSON, Markdown, Text).

```
AdNova/
├── main.py                 # Entry point for the application
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── config/
│   └── settings.py         # Configuration settings (API keys, model parameters)
├── core/
│   ├── agent.py            # Core agent implementation
│   ├── memory.py           # Agent memory management
│   ├── planning.py         # Task planning and decomposition for complex requests
│   └── reflection.py       # Self-improvement through feedback
├── tools/
│   ├── ad_generator.py     # Ad generation tool
│   ├── audience_analyzer.py # Audience analysis tool
│   ├── brand_voice.py      # Brand voice definition and maintenance
│   └── feedback_processor.py # Process client feedback
├── ui/
│   ├── cli.py              # Command-line interface
│   ├── web_app.py          # Web application (Streamlit)
│   └── templates/          # Web UI templates
├── data/
│   ├── campaign_briefs/    # Storage for campaign briefs
│   ├── generated_ads/      # Storage for generated ads
│   └── feedback/           # Storage for client feedback
└── utils/
    ├── api_utils.py        # Utilities for API interactions
    ├── text_processing.py  # Text processing utilities
    └── validators.py       # Input validation functions
```

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API key

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/marketing-ad-agent.git
   cd marketing-ad-agent
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

**NOTE:** When commiting to this repo, please do not commit the `.env` file. You can use the following commands to ensure this:

```
git rm --cached config/.env
echo "config/.env" >> .gitignore
git add .gitignore
git add -A
git commit -m "Your commit message here"
git push
```

## Usage

### Starting the Application

The application can be run in either CLI or web mode:

**Web Interface (recommended):**
```
python main.py --mode web
```

**Command Line Interface:**
```
python main.py --mode cli
```

### Workflow

1. **Create a Campaign Brief**: Define your product, target audience, and campaign goals.
2. **Generate Ads**: Choose from various ad formats to generate tailored marketing content.
3. **Review and Provide Feedback**: Evaluate the generated ads and provide feedback.
4. **Regenerate Improved Ads**: Use the feedback to create improved versions.
5. **Export Campaign Assets**: Export all your marketing content for use in other systems.

## Web Interface

The web interface provides a user-friendly way to interact with the Marketing Ad Agent. It includes the following sections:

- **Create Brief**: Define campaign parameters and analyze target audience.
- **Generate Ads**: Create ads in various formats based on your campaign brief.
- **View Ads**: Browse all generated ads organized by campaign.
- **Feedback & Improvement**: Provide feedback and regenerate improved ads.
- **Analytics & Insights**: View campaign metrics and audience insights.
- **Export**: Export campaign assets in various formats.

## LLM Model Selection

This implementation uses **GPT-4** as the primary model because:

- It has strong creative writing capabilities essential for compelling ad copy
- It understands marketing concepts, audience psychology, and brand voice well
- It can generate diverse ad formats with the right tone and messaging
- It can take marketing-specific instructions and adapt to different brand voices
- It has sufficient context window to handle campaign briefs and reference materials

## System Architecture

The system is organized into several key components:

- **Core**: The central agent logic, memory management, planning, and self-reflection.
- **Tools**: Specialized components for ad generation, audience analysis, brand voice, and feedback processing.
- **UI**: Command-line and web-based user interfaces.
- **Utils**: Helper utilities for API interactions, text processing, and validation.
- **Config**: Configuration settings for the application.

## Data Storage

The system stores all data locally in these directories:

- `data/campaign_briefs`: Campaign definitions and audience insights
- `data/generated_ads`: Generated ad content in various formats
- `data/feedback`: Client feedback and processed insights
- `data/insights`: Derived insights and improvement suggestions
- `data/brand_voices`: Brand voice definitions
- `data/exports`: Exported campaign assets

## Customization

### Adding New Ad Types

To add a new ad format:

1. Add a new generator method in `tools/ad_generator.py`
2. Update the available ad types in `config/settings.py`
3. Update the UI to include the new ad type option

### Extending Functionality

The modular design allows for easy extension:

- Add new analysis tools in the `tools` directory
- Implement additional export formats in the agent's export method
- Enhance feedback processing with more advanced sentiment analysis

## Limitations

- Content is generated based on provided information only - real market research is still valuable
- Performance depends on the quality of the initial brief and prompt
- Some complex brand identity aspects may need human refinement
- Real ad performance metrics require actual market testing

## License

[MIT License](LICENSE)
