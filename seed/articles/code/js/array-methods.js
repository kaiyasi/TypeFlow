// JavaScript - Array Methods Practice

// Basic array operations
const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

// Filter even numbers
const evenNumbers = numbers.filter(num => num % 2 === 0);
console.log('Even numbers:', evenNumbers);

// Map to squares
const squares = numbers.map(num => num * num);
console.log('Squares:', squares);

// Reduce to sum
const sum = numbers.reduce((acc, num) => acc + num, 0);
console.log('Sum:', sum);

// Complex example: Shopping cart
const cart = [
  { name: 'Laptop', price: 999.99, quantity: 1 },
  { name: 'Mouse', price: 29.99, quantity: 2 },
  { name: 'Keyboard', price: 79.99, quantity: 1 },
  { name: 'Monitor', price: 299.99, quantity: 1 }
];

// Calculate total price
const totalPrice = cart.reduce((total, item) => {
  return total + (item.price * item.quantity);
}, 0);

console.log(`Total cart value: $${totalPrice.toFixed(2)}`);

// Find expensive items (over $100)
const expensiveItems = cart.filter(item => item.price > 100);
console.log('Expensive items:', expensiveItems);

// Create item list with formatted prices
const itemList = cart.map(item => ({
  ...item,
  formattedPrice: `$${item.price.toFixed(2)}`,
  totalItemPrice: `$${(item.price * item.quantity).toFixed(2)}`
}));

console.log('Formatted cart:', itemList);