# Airplane Design Cascade Optimizer

An interactive web application for running OpenMDAO airplane design cascade models with adjustable parameters.

## Features

- 🎯 **Single Point Analysis**: Run the model with specific windshield size
- 📊 **Parametric Sweep**: Analyze model behavior across a range of sizes
- 📈 **Interactive Visualizations**: Real-time plots using Plotly
- 💾 **Export Results**: Download CSV data from parametric sweeps
- 🚀 **Free Hosting**: Deploy for free on Streamlit Cloud or Render

## Quick Start (Local)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
streamlit run app.py
```

3. Open your browser to `http://localhost:8501`

## Deploy for FREE on Streamlit Cloud (Recommended)

### Step-by-Step Instructions:

1. **Create a GitHub Account** (if you don't have one)
   - Go to https://github.com
   - Sign up for free

2. **Create a New Repository**
   - Click the "+" icon → "New repository"
   - Name it: `airplane-optimizer` (or any name you like)
   - Make it Public
   - Don't initialize with README (we'll upload files)
   - Click "Create repository"

3. **Upload Your Files to GitHub**
   - On your new repository page, click "uploading an existing file"
   - Drag and drop these 3 files:
     * `app.py`
     * `requirements.txt`
     * `README.md` (this file)
   - Click "Commit changes"

4. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Click "Sign in" and use your GitHub account
   - Click "New app"
   - Select your repository: `airplane-optimizer`
   - Main file path: `app.py`
   - Click "Deploy!"

5. **Done!** 🎉
   - Your app will be live at: `https://[your-app-name].streamlit.app`
   - Deployment takes 2-3 minutes
   - You can share this URL with anyone!

## Alternative: Deploy on Render.com (Also Free)

1. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     * Name: `airplane-optimizer`
     * Environment: `Python 3`
     * Build Command: `pip install -r requirements.txt`
     * Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
   - Select "Free" plan
   - Click "Create Web Service"

3. **Access Your App**
   - Will be available at: `https://airplane-optimizer.onrender.com`
   - First deployment takes 5-10 minutes
   - Free tier may sleep after inactivity (takes 30s to wake up)

## Using the Application

### Single Point Analysis
1. Select "Single Point" mode
2. Adjust windshield size slider
3. Click "Run Analysis"
4. View results and cascade flow diagram

### Parametric Sweep
1. Select "Parametric Sweep" mode
2. Set minimum and maximum sizes
3. Choose number of analysis points
4. Click "Run Analysis"
5. View interactive plot and download CSV data

## Model Description

The cascade model simulates the design trade-offs in airplane windshield sizing:

1. **Thermal Component**: Larger windshields generate more heat load
2. **Cooling System**: More heat requires heavier cooling systems
3. **Performance**: Weight and drag increase fuel consumption

### Equations
- Heat Load = 2.5 × Windshield Size + 10
- System Weight = 0.5 × Heat Load + 50
- Fuel Burn = 0.8 × System Weight + 1.2 × Windshield Size

## Customization

You can modify the model by editing `app.py`:

- Change equations in the `compute()` methods
- Add new components to the cascade
- Modify the UI layout and styling
- Add optimization capabilities

## Troubleshooting

**App won't start locally?**
- Make sure Python 3.8+ is installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`

**Deployment failed?**
- Check that all files are in the repository root
- Verify `requirements.txt` has no syntax errors
- Streamlit Cloud: Check build logs in the app dashboard
- Render: Check deployment logs

**Want to add optimization?**
- OpenMDAO supports optimization out of the box
- Add a driver (e.g., `om.ScipyOptimizeDriver()`)
- Define design variables and constraints
- Example: Minimize fuel burn by optimizing windshield size

## Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [OpenMDAO Documentation](https://openmdao.org/newdocs/versions/latest/main.html)
- [Plotly Python](https://plotly.com/python/)

## License

This project is open source and free to use.