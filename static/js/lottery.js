const resetBtn = document.querySelector('.reset');
let interval;
let count = 0;

// start the timer when page loads
//createTimer();

// recreate the timer when reset is clicked
resetBtn.addEventListener('click', createTimer);

// create the interval that creates the timer
function createTimer() {
  document.getElementById('finalimg').style.display = 'none';
  // document.getElementById('counter').style.visibility = 'visible';
  document.getElementById('counter').style.display = 'block';
  countdownArea = document.querySelector('.countdown');
  numbersArea = document.querySelector('.numbers');
  height = countdownArea.getBoundingClientRect().height;

  clearInterval(interval);
  count = 0;
  numbersArea.style.transform = 'translateY(0)'

  interval = setInterval(() => {
    count++;

    // calculate the offset and apply it
    const offset = height * count;
    numbersArea.style.transform = `translateY(-${offset}px)`

    // what happens when countdown is done
    if (count >= 11) {
      // go to the next episode
      clearInterval(interval);
      // document.getElementById('winner').style.visibility = 'visible';
      document.getElementById('winner').style.display = 'block';
      document.getElementById("countbtn").style.display = 'none';      // document.getElementById('count').style.visibility = 'hidden';
    }
  }, 1000);
}
