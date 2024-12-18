# ▶️ Video Fact Finder

This project analyzes a YouTube video and provides a summarized version of the content. 
Simply input the YouTube URL, and the OpenAI and Perplexity agents handle the rest.

## Deliverables

All deliverables for this project are located in the `deliverables` folder. 
Please see below for the list of deliverables:

1. `CMPE297_BayAreaRockers_FinalProject_Report.pdf`: The PDF file for the final report for the project.
2. `CMPE297_BayAreaRockers_FinalProject_SlideDeck.pdf`: The PDF file for the slide deck for the project.
3. [Slide Deck and Demo Videoo](https://www.youtube.com): A video showcasing the slide deck and demo of the application.

## Setup

Before running the application, add your API keys in a `.env` file (Note: there are no quotes around the keys).

```bash
# Contents of .env file below:
OPENAI_API_KEY=REPLACEME
PPLX_API_KEY=REPLACEME
```

### Instructions To Run Application

The following instructions assume that you are running docker on your local machine. 
You are also expected to be able to run docker-compose commands. 

1. Clone the repository:
`git clone https://github.com/schumbar/CMPE297_final_project`

2. Change directory to the project folder:
`cd <path_to_cloned_repo>/CMPE297_final_project/`

3. Verify that docker desktop is running on your machine. You will probably just need to run the application and verify that docker desktop window shows up.

4. Run the following command to build and run the docker image:
`docker-compose up --build`

5. Open a new browser window and navigate to the following URL:
`http://localhost:8501`

6. When you are done using the application, you can stop the docker container by pressing `CTRL+C` in the terminal where you ran the `docker-compose up --build` command.

## Usage

1. Enter the YouTube URL in the input field.
For example:
https://www.youtube.com/watch?v=7E9uMZYTMU8
