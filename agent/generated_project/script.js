// Calculator Application Logic
// This script implements the core functionality, UI interaction, and keyboard support
// for the simple calculator defined in index.html.

// 1. Global constants & DOM references
const display = document.getElementById('display');
const buttons = document.querySelectorAll('.btn');

// 2. Calculator class – encapsulates state and behavior
class Calculator {
  /**
   * Creates a new Calculator instance bound to a display element.
   * @param {HTMLInputElement} displayElement - The input element used as the calculator display.
   */
  constructor(displayElement) {
    this.displayElement = displayElement;
    this.clear();
  }

  /** Reset the calculator to its initial state. */
  clear() {
    this.currentOperand = '';
    this.previousOperand = '';
    this.operation = undefined;
    this.updateDisplay();
  }

  /** Optional future feature – delete the last digit. */
  delete() {
    this.currentOperand = this.currentOperand.toString().slice(0, -1);
    this.updateDisplay();
  }

  /** Append a number or decimal point to the current operand. */
  appendNumber(number) {
    // Prevent multiple decimals in the same operand
    if (number === '.' && this.currentOperand.includes('.')) return;
    this.currentOperand = this.currentOperand.toString() + number.toString();
    this.updateDisplay();
  }

  /** Choose an arithmetic operation (+, -, *, /). */
  chooseOperation(operation) {
    if (this.currentOperand === '') return;
    // If there is already a previous operand, compute the intermediate result first
    if (this.previousOperand !== '') {
      this.compute();
    }
    this.operation = operation;
    this.previousOperand = this.currentOperand;
    this.currentOperand = '';
    this.updateDisplay();
  }

  /** Perform the calculation based on the stored operands and operation. */
  compute() {
    const prev = parseFloat(this.previousOperand);
    const current = parseFloat(this.currentOperand);
    if (isNaN(prev) || isNaN(current)) return;
    let computation;
    switch (this.operation) {
      case '+':
        computation = prev + current;
        break;
      case '-':
        computation = prev - current;
        break;
      case '*':
        computation = prev * current;
        break;
      case '/':
        if (current === 0) {
          computation = 'Error'; // division by zero handling
        } else {
          computation = prev / current;
        }
        break;
      default:
        return;
    }
    this.currentOperand = computation.toString();
    this.operation = undefined;
    this.previousOperand = '';
    this.updateDisplay();
  }

  /** Update the calculator display element with the current value. */
  updateDisplay() {
    // Prefer showing the current operand; fallback to previous operand or 0
    this.displayElement.value = this.currentOperand || this.previousOperand || '0';
  }
}

// 3. Instantiate the calculator after DOM elements are queried
const calculator = new Calculator(display);

// 4. Button event handling – delegate clicks based on data-value attribute
buttons.forEach(btn => {
  btn.addEventListener('click', () => {
    const value = btn.dataset.value;
    if (!value) return;
    // Number or decimal point
    if ((value >= '0' && value <= '9') || value === '.') {
      calculator.appendNumber(value);
    } else if (value === 'C') {
      calculator.clear();
    } else if (value === '=') {
      calculator.compute();
    } else {
      // Operators: +, -, *, /
      calculator.chooseOperation(value);
    }
  });
});

// 5. Keyboard support – map physical keys to calculator actions
document.addEventListener('keydown', e => {
  const key = e.key;
  if ((key >= '0' && key <= '9') || key === '.') {
    e.preventDefault();
    calculator.appendNumber(key);
  } else if (key === '+' || key === '-' || key === '*' || key === '/') {
    e.preventDefault();
    calculator.chooseOperation(key);
  } else if (key === 'Enter' || key === '=') {
    e.preventDefault();
    calculator.compute();
  } else if (key === 'Escape' || key.toLowerCase() === 'c') {
    e.preventDefault();
    calculator.clear();
  }
});
