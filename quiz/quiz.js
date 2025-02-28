let dataset = [
    { f: "Data not loaded...", m: "circunstancial", s: "ixé", o: "xé" },
    // Add more sentences and information here
];

let easy_dataset = [
    { f: "Data not loaded...", m: "circunstancial", s: "ixé", o: "xé" },
    // Add more sentences and information here
];

let hard_dataset = [
    { f: "Data not loaded...", m: "circunstancial", s: "ixé", o: "xé" },
    // Add more sentences and information here
];

let currentQuestionIndex = 0;
let score = 0;
let question_count = 5;
let modes = ['Present'];
let enviarButton = document.getElementById('enviar');
let isHardMode = false;
let toggleDifficulty = null;

function loadCompressedJSONSync(bytes) {
    var decompressedData = pako.inflate(bytes, { to: 'string' });
    return JSON.parse(decompressedData);
}

function loadJSONSync(url) {
    var xhr = new XMLHttpRequest();
    // xhr.overrideMimeType("application/json");
    xhr.open('GET', url, false); // Make the request synchronous
    xhr.send(null);
    if (xhr.readyState == 4 && xhr.status == 200) {
        return JSON.parse(xhr.responseText);
    }
    return null;
}

function startQuiz() {
    function applyHardMode() {
        console.log("Hard Mode");
        dataset = hard_dataset;
    }
    
    // Adjust settings for Easy Mode
    function applyEasyMode() {
        console.log("Easy Mode");
        dataset = easy_dataset;
    }
    // Ensure initial mode is applied
    document.addEventListener("DOMContentLoaded", () => {
        const modeButton = document.getElementById("difficulty-toggle");
        modeButton.classList.add("easy-mode");
    });
    
    // Ensure difficulty mode is applied when quiz starts
    document.addEventListener("DOMContentLoaded", () => {
        applyEasyMode();
    });
    // Load the dataset from 'verbs.json'
    fetch('quiz.json.gz')
        .then(response => response.arrayBuffer())
        .then(data => {
            // Assign the loaded data to the dataset variable
            hard_dataset = loadCompressedJSONSync(data);

            // hard_dataset = hard_dataset.filter(item => item.c !== undefined);
            console.log(hard_dataset);
            // copy the item.f field to a new item.n field in the hard_dataset
            hard_dataset.forEach(item => {
                item.n = item.f;
            });
            // hard_dataset = hard_dataset.flatMap(item => item.c);
            // Shuffle the hard_dataset
            // dataset = hard_dataset;
            shuffleDataset();

            // Populate dropdown options
            populateDropdown('tense', ["Present"]);
            populateDropdown('subject', ['I', 'You', 'He/She', 'We','We+', "Y'all","Y'all+", "They","They+"]);
            populateDropdown('object',  ['ø', 'Me', 'You', 'Him/Her', 'Us', "Y'all", "Them"]);

            showQuestion();
        })
        .catch(error => {
            console.error('Error loading dataset:', error);
        });
        let easy_raw = loadJSONSync('/muscogee/quiz_easymode.json');
        console.log("easy_raw", easy_raw);
        easy_dataset = Array();
        // for each object in the list of easy_raw, if the con object is a list, add each object in the list to the easy_dataset
        for (let i = 0; i < easy_raw.length; i++) {
            if (easy_raw[i][0].c) {
                easy_dataset = easy_dataset.concat(easy_raw[i][0].c);
            }
        }
        console.log("easy", easy_dataset);
        dataset = easy_dataset;
        // Adjust settings for Hard Mode
        // Easy mode
        toggleDifficulty = function() {
            isHardMode = !isHardMode;
            const modeButton = document.getElementById("difficulty-toggle");
        
            if (isHardMode) {
                modeButton.textContent = "Hard Mode";
                modeButton.classList.remove("easy-mode");
                modeButton.classList.add("hard-mode");
                applyHardMode();
            } else {
                modeButton.textContent = "Easy Mode";
                modeButton.classList.remove("hard-mode");
                modeButton.classList.add("easy-mode");
                applyEasyMode();
            }
        }
        applyEasyMode();

}

function restartQuiz() {
    currentQuestionIndex = 0;
    score = 0;
    shuffleDataset();
    showQuestion();
    document.getElementById('result-container').style.display = 'none';
    document.getElementById('quiz-container').style.display = 'block';
}

function shuffleDataset() {
    for (let i = dataset.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [dataset[i], dataset[j]] = [dataset[j], dataset[i]];
    }
}

function populateDropdown(id, options) {
    const dropdown = document.getElementById(id);
    
    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option;
        optionElement.text = option;
        dropdown.add(optionElement);
    });
    dropdown.value = options[0];
}

// Select the checkbox element
const autoSoundCheckbox = document.getElementById('autoSound');

// Function to get the checked value
function isAutoSoundEnabled() {
  return autoSoundCheckbox.checked; // Returns true if checked, false otherwise
}

let filteredDataset = [];
let audio = new Audio();
function showQuestion() {
    enviarButton.style.display = 'block';
    const progressFeedback = document.getElementById('progress-feedback');
    progressFeedback.innerText = `Questions: ${currentQuestionIndex+1}/${question_count}`;

    resetDropdowns();
    if (currentQuestionIndex < question_count) {
        // Filter the dataset based on active mood buttons
        const activeMoodButtons = document.querySelectorAll('.mood-button-active');
        const activeMoods = Array.from(activeMoodButtons).map(button => button.id);
        filteredDataset = dataset.filter(item => activeMoods.includes(item.m));
        console.log(activeMoods);
        // Generate the next question using the filtered dataset
        const currentQuestion = filteredDataset[currentQuestionIndex];
        document.getElementById('question').innerText = currentQuestion.f;
        partsArray = currentQuestion.d.split(' -');
        mode_val = modes.find(option => option.slice(0, 4).toLocaleLowerCase() == currentQuestion.m);
        console.log(mode_val)
        document.getElementById('definition').href = `https://www.nokose-oklane.com/conjugations/action_verb?word=${encodeURIComponent(partsArray[0])}&search=Search&key=mus&search_options_set=1&match_whole_words=1&match_accents=on`;
        // Add button for audio
        audio.src = currentQuestion.surl;
        if (currentQuestion.surl == null) {
            document.getElementById('definition-audio').style.display = 'none';
        } else {
            document.getElementById('definition-audio').style.display = 'block';
        }
        document.getElementById('definition-audio').onclick = function() {
            audio.play();
        }
        document.getElementById('definition').innerText = partsArray[0];
        document.getElementById('definition-text').innerText = partsArray.slice(1).join(' -');
        document.getElementById('response').innerText = 'Tense: ' + mode_val + '; Subject: ' + reverseSubjPrefMap[currentQuestion.s] + '; Object: ' + reverseObjPrefMap[currentQuestion.o] + ';';
    } else {
        showResult();
    }
}

function submitAnswer(event) {
    enviarButton.style.display = 'none';
    answers = document.querySelectorAll('.answer-container');
    answers.forEach(answer => {
        answer.style.display = 'block';
    });
    const mode = document.getElementById('tense');
    const subject = document.getElementById('subject');
    const object = document.getElementById('object');

    if (isAutoSoundEnabled()) {
        audio.play();
    }

    checkDropdownAnswer('mode', mode);
    checkDropdownAnswer('subject', subject);
    checkDropdownAnswer('object', object);

    // Move to the next question
    currentQuestionIndex++;
}

function resetDropdowns() {
    answers = document.querySelectorAll('.answer-container');
    answers.forEach(answer => {
        answer.style.display = 'none';
    });
    // Reset dropdowns to their default values
    document.getElementById('tense').value = 'Present';
    document.getElementById('subject').value = 'I';
    document.getElementById('object').value = 'ø';
    // Reset the border color of all dropdowns to default
    dropdowns = document.querySelectorAll('.option');
    dropdowns.forEach(dropdown => {
        dropdown.style.backgroundColor = '#4caf50'; // Set your default border color
    });
}

let subj_pref_map = {
    'ø': null,
    'I': '1ps',
    'We': '1pp',
    'We+': '1pp+',
    'They': '3pp',
    'They+': '3pp+',
    'You': '2ps',
    "Y'all": '2pp',
    "Y'all+": '2pp+',
    "He/She": '3ps'
}
let obj_pref_map = {
    'ø': null,
//'Me', 'You', 'Him/Her', 'Us', "Y'all", "Them"
    'Me': '1ps',
    'Us': '1pp',
    'You': '2ps',
    "Y'all": '2pp',
    'Him/Her': '3ps',
    'Them': '3pp'
} 

// Function to create a reverse map
function createReverseMap(inputMap) {
    let reverseMap = {};
    for (let key in inputMap) {
        if (inputMap.hasOwnProperty(key)) {
            let value = inputMap[key];
            if (value !== null) {
                reverseMap[value] = key;
            }
        }
    }
    return reverseMap;
}

// Create reverse maps
let reverseSubjPrefMap = createReverseMap(subj_pref_map);
let reverseObjPrefMap = createReverseMap(obj_pref_map);

function checkDropdownAnswer(part, dropdownElement) {
    selectedValue = dropdownElement.value;
    const currentQuestion = filteredDataset[currentQuestionIndex];
    is_correct = false;
    // console.log(part, selectedValue, selectedValue.substring(0, 2), currentQuestion.m)
    if (part === 'mode' && selectedValue.substring(0, 4).toLocaleLowerCase() === currentQuestion.m) {
        score++;
        is_correct = true;
    } else if (part === 'subject' && subj_pref_map[selectedValue] === currentQuestion.s) {
        is_correct = true;
        score++;
    } else if (part === 'object' && obj_pref_map[selectedValue] === currentQuestion.o) {
        is_correct = true;
        score++;
    }
    if(!is_correct) {
        dropdownElement.style.backgroundColor = 'red';
    }
    console.log(score, currentQuestion);
}

function showResult() {
    document.getElementById('quiz-container').style.display = 'none';
    const resultContainer = document.getElementById('result-container');
    resultContainer.style.display = 'block';
    console.log("audio source: ", audio.src);

    document.getElementById('score').innerText = `Your score is: ${score} out of ${question_count*3}`;
}

document.addEventListener("DOMContentLoaded", function () {
    // Your JavaScript code here
    startQuiz();
    resetDropdowns();
});

document.querySelectorAll('.mood-button').forEach(button => {
    button.addEventListener('click', () => {
        button.classList.toggle('mood-button-active');
    });
});


