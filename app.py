from flask import Flask, request, jsonify, render_template_string
import requests
import json
import re

app = Flask(__name__)

# HTML Template with Image & Diagram Support
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Visual Assistant - Answers with Images</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            height: 100vh;
        }

        .container {
            display: flex;
            height: 100vh;
            max-width: 1400px;
            margin: 0 auto;
        }

        /* Sidebar */
        .sidebar {
            width: 280px;
            background: white;
            border-right: 1px solid #e2e8f0;
            display: flex;
            flex-direction: column;
        }

        .sidebar-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }

        .sidebar-header h2 {
            font-size: 1.3rem;
        }

        .features {
            flex: 1;
            padding: 20px;
        }

        .feature-btn {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            background: #f1f5f9;
            border: none;
            border-radius: 10px;
            text-align: left;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
        }

        .feature-btn:hover {
            background: #667eea;
            color: white;
            transform: translateX(5px);
        }

        /* Main Chat Area */
        .main-chat {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #f8fafc;
        }

        .chat-header {
            background: white;
            padding: 20px;
            border-bottom: 1px solid #e2e8f0;
            text-align: center;
        }

        .chat-header h1 {
            font-size: 1.5rem;
            color: #1e293b;
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }

        .message {
            margin-bottom: 20px;
            animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .user-message {
            text-align: right;
        }

        .bot-message {
            text-align: left;
        }

        .message-content {
            display: inline-block;
            max-width: 80%;
            padding: 12px 18px;
            border-radius: 18px;
            word-wrap: break-word;
        }

        .user-message .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .bot-message .message-content {
            background: white;
            color: #1e293b;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
            text-align: left;
        }

        /* Image Styles */
        .answer-image {
            max-width: 100%;
            margin: 15px 0;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .diagram-container {
            background: #f8fafc;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            text-align: center;
        }

        .code-block {
            background: #1e293b;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 10px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            margin: 10px 0;
        }

        .algorithm-visual {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            border: 1px solid #e2e8f0;
        }

        .array-visual {
            display: flex;
            gap: 5px;
            justify-content: center;
            flex-wrap: wrap;
            margin: 10px 0;
        }

        .array-element {
            background: #667eea;
            color: white;
            padding: 10px;
            min-width: 50px;
            text-align: center;
            border-radius: 8px;
            font-weight: bold;
        }

        .input-area {
            padding: 20px;
            background: white;
            border-top: 1px solid #e2e8f0;
            display: flex;
            gap: 10px;
        }

        input {
            flex: 1;
            padding: 12px 18px;
            border: 2px solid #e2e8f0;
            border-radius: 25px;
            outline: none;
            font-size: 14px;
        }

        input:focus {
            border-color: #667eea;
        }

        button {
            padding: 12px 28px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s;
        }

        button:hover {
            transform: scale(1.02);
        }

        .typing {
            display: inline-block;
            width: 40px;
            text-align: center;
        }

        .typing span {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #94a3b8;
            margin: 0 2px;
            animation: typing 1.4s infinite;
        }

        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }

        @media (max-width: 768px) {
            .sidebar {
                display: none;
            }
            .message-content {
                max-width: 95%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>🎨 Visual Assistant</h2>
                <p>Answers with images & diagrams</p>
            </div>
            <div class="features">
                <button class="feature-btn" onclick="askQuestion('Show me how heap sort works with visualization')">
                    📊 Heap Sort Visualization
                </button>
                <button class="feature-btn" onclick="askQuestion('Draw a binary tree diagram for heap sort')">
                    🌳 Binary Tree Diagram
                </button>
                <button class="feature-btn" onclick="askQuestion('Show me the time complexity comparison of sorting algorithms with a chart')">
                    📈 Complexity Chart
                </button>
                <button class="feature-btn" onclick="askQuestion('Explain quick sort with a visual example')">
                    ⚡ Quick Sort Visual
                </button>
                <button class="feature-btn" onclick="askQuestion('Draw a flowchart for binary search algorithm')">
                    🔍 Binary Search Flowchart
                </button>
                <button class="feature-btn" onclick="askQuestion('Show me how a neural network works with diagram')">
                    🧠 Neural Network Diagram
                </button>
                <button class="feature-btn" onclick="askQuestion('Visually explain bubble sort with animation')">
                    🫧 Bubble Sort Visual
                </button>
                <button class="feature-btn" onclick="askQuestion('Show me data structure hierarchy tree')">
                    🌲 Data Structure Tree
                </button>
            </div>
        </div>

        <!-- Main Chat -->
        <div class="main-chat">
            <div class="chat-header">
                <h1>🤖 AI Visual Assistant</h1>
                <p>Ask any question - Get answers with images, diagrams, and code</p>
            </div>

            <div class="chat-messages" id="chatMessages">
                <div class="message bot-message">
                    <div class="message-content">
                        <strong>👋 Hello! I'm your visual AI assistant!</strong><br><br>
                        I can answer questions with:<br>
                        • 📊 Visual diagrams and charts<br>
                        • 🌳 Tree structures and algorithms<br>
                        • 💻 Code with explanations<br>
                        • 📈 Complexity graphs<br>
                        • 🎨 Interactive visualizations<br><br>
                        <strong>Try asking:</strong><br>
                        "Show me heap sort visualization"<br>
                        "Explain binary tree with diagram"<br>
                        "Draw sorting algorithm comparison"
                    </div>
                </div>
            </div>

            <div class="input-area">
                <input type="text" id="userInput" placeholder="Ask anything... Examples: 'Show me heap sort', 'Draw binary tree', 'Explain quick sort visually'" onkeypress="if(event.key=='Enter') sendMessage()">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        const chatMessages = document.getElementById('chatMessages');
        
        function askQuestion(question) {
            document.getElementById('userInput').value = question;
            sendMessage();
        }
        
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            if (!message) return;
            
            // Add user message
            addMessage(message, 'user');
            input.value = '';
            
            // Show typing indicator
            showTyping();
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                removeTyping();
                
                if (data.response) {
                    addRichMessage(data.response, data.image_type, data.image_data);
                } else {
                    addMessage('Sorry, I encountered an error. Please try again.', 'bot');
                }
            } catch (error) {
                removeTyping();
                addMessage('Error: Could not connect to server.', 'bot');
            }
        }
        
        function addMessage(text, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.innerHTML = text.replace(/\\n/g, '<br>');
            messageDiv.appendChild(contentDiv);
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function addRichMessage(text, imageType, imageData) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot-message';
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            // Add text content
            contentDiv.innerHTML += text.replace(/\\n/g, '<br>');
            
            // Add image if provided
            if (imageData) {
                const img = document.createElement('img');
                img.src = imageData;
                img.className = 'answer-image';
                img.style.maxWidth = '100%';
                img.style.marginTop = '15px';
                img.style.borderRadius = '10px';
                contentDiv.appendChild(img);
            }
            
            messageDiv.appendChild(contentDiv);
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function showTyping() {
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message bot-message';
            typingDiv.id = 'typingIndicator';
            typingDiv.innerHTML = '<div class="message-content"><div class="typing"><span></span><span></span><span></span></div></div>';
            chatMessages.appendChild(typingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function removeTyping() {
            const indicator = document.getElementById('typingIndicator');
            if (indicator) indicator.remove();
        }
    </script>
</body>
</html>
"""

# Knowledge base with answers and images
def get_answer_with_image(question):
    question_lower = question.lower()
    
    # Heap Sort with Visualization
    if 'heap sort' in question_lower:
        return {
            'text': """
                <strong>📊 Heap Sort - Complete Guide with Visualization</strong><br><br>
                
                <strong>What is Heap Sort?</strong><br>
                Heap sort is a comparison-based sorting algorithm that uses a binary heap data structure. It's like organizing a tournament where the largest element "wins" and gets placed at the end.<br><br>
                
                <strong>🎯 How it works (Simple Explanation):</strong><br>
                1. <strong>Build a Heap:</strong> Arrange the array into a special tree structure called a "heap" (like a pyramid where parent is larger than children)<br>
                2. <strong>Extract Maximum:</strong> Take the largest element from the top<br>
                3. <strong>Repeat:</strong> Put it at the end and fix the heap<br>
                4. <strong>Continue</strong> until all elements are sorted<br><br>
                
                <strong>⏱️ Time Complexity:</strong><br>
                • Best Case: O(n log n)<br>
                • Average Case: O(n log n)<br>
                • Worst Case: O(n log n)<br>
                • Space Complexity: O(1) - sorts in-place!<br><br>
                
                <strong>💻 C++ Code:</strong>
                <div class='code-block'>
// Heap Sort Implementation in C++
#include &lt;iostream&gt;
using namespace std;

// Heapify function - maintains heap property
void heapify(int arr[], int n, int i) {
    int largest = i;     // Root
    int left = 2*i + 1;  // Left child
    int right = 2*i + 2; // Right child
    
    // If left child is larger than root
    if (left < n && arr[left] > arr[largest])
        largest = left;
    
    // If right child is larger than largest
    if (right < n && arr[right] > arr[largest])
        largest = right;
    
    // If largest is not root
    if (largest != i) {
        swap(arr[i], arr[largest]);
        heapify(arr, n, largest);  // Recursively heapify
    }
}

// Main heap sort function
void heapSort(int arr[], int n) {
    // Build heap (rearrange array)
    for (int i = n/2 - 1; i >= 0; i--)
        heapify(arr, n, i);
    
    // Extract elements one by one
    for (int i = n-1; i > 0; i--) {
        swap(arr[0], arr[i]);  // Move current root to end
        heapify(arr, i, 0);    // Heapify reduced heap
    }
}

// Print array
void printArray(int arr[], int n) {
    for (int i = 0; i < n; i++)
        cout << arr[i] << " ";
    cout << endl;
}

// Driver code
int main() {
    int arr[] = {12, 11, 13, 5, 6, 7};
    int n = sizeof(arr)/sizeof(arr[0]);
    
    cout << "Original array: ";
    printArray(arr, n);
    
    heapSort(arr, n);
    
    cout << "Sorted array: ";
    printArray(arr, n);
    return 0;
}
                </div>
                
                <strong>🔍 Step-by-Step Example:</strong><br>
                Array: [12, 11, 13, 5, 6, 7]<br><br>
                
                <strong>Step 1 - Build Max Heap:</strong> [13, 11, 12, 5, 6, 7]<br>
                <strong>Step 2 - Swap 13 with 7:</strong> [7, 11, 12, 5, 6, 13]<br>
                <strong>Step 3 - Heapify:</strong> [12, 11, 7, 5, 6, 13]<br>
                <strong>Step 4 - Swap 12 with 6:</strong> [6, 11, 7, 5, 12, 13]<br>
                <strong>Step 5 - Heapify:</strong> [11, 6, 7, 5, 12, 13]<br>
                <strong>Step 6 - Continue until sorted:</strong> [5, 6, 7, 11, 12, 13]<br><br>
                
                <div class='algorithm-visual'>
                    <strong>📊 Heap Sort Visualization:</strong><br>
                    <div class='array-visual'>
                        <div class='array-element'>13</div>
                        <div class='array-element'>11</div>
                        <div class='array-element'>12</div>
                        <div class='array-element'>5</div>
                        <div class='array-element'>6</div>
                        <div class='array-element'>7</div>
                    </div>
                    <div style='text-align: center;'>↓ After heapify ↓</div>
                    <div class='array-visual'>
                        <div class='array-element'>13</div>
                        <div class='array-element'>11</div>
                        <div class='array-element'>12</div>
                        <div class='array-element'>5</div>
                        <div class='array-element'>6</div>
                        <div class='array-element'>7</div>
                    </div>
                    <div style='text-align: center;'>↓ Sorted ↓</div>
                    <div class='array-visual'>
                        <div class='array-element' style='background: #48bb78;'>5</div>
                        <div class='array-element' style='background: #48bb78;'>6</div>
                        <div class='array-element' style='background: #48bb78;'>7</div>
                        <div class='array-element' style='background: #48bb78;'>11</div>
                        <div class='array-element' style='background: #48bb78;'>12</div>
                        <div class='array-element' style='background: #48bb78;'>13</div>
                    </div>
                </div>
                
                <strong>✅ Advantages:</strong><br>
                • Efficient O(n log n) performance<br>
                • In-place sorting (no extra memory)<br>
                • Consistent performance regardless of input<br>
                • Great for embedded systems<br><br>
                
                <strong>❌ Disadvantages:</strong><br>
                • Not stable (equal elements may change order)<br>
                • More complex than quick sort or merge sort<br>
                • Poor cache performance<br>
            """,
            'image_type': None,
            'image_data': None
        }
    
    # Binary Tree Diagram
    elif 'binary tree' in question_lower or 'tree diagram' in question_lower:
        return {
            'text': """
                <strong>🌳 Binary Tree - Complete Guide with Diagram</strong><br><br>
                
                <strong>What is a Binary Tree?</strong><br>
                A binary tree is a hierarchical data structure where each node has at most 2 children (left and right).<br><br>
                
                <div class='diagram-container'>
                    <strong>📊 Binary Tree Structure:</strong><br><br>
                    <div style='font-family: monospace; text-align: center;'>
                        10<br>
                       /  \\<br>
                      5    15<br>
                     / \\  / \\<br>
                    3   7 12 20<br>
                    </div>
                </div>
                
                <strong>🏷️ Tree Terminology:</strong><br>
                • <strong>Root:</strong> Top node (10)<br>
                • <strong>Parent:</strong> Node with children (5 is parent of 3 and 7)<br>
                • <strong>Child:</strong> Node below another (3 and 7 are children of 5)<br>
                • <strong>Leaf:</strong> Nodes with no children (3, 7, 12, 20)<br>
                • <strong>Height:</strong> Number of edges from root to deepest leaf (2)<br><br>
                
                <strong>💻 C++ Implementation:</strong>
                <div class='code-block'>
struct Node {
    int data;
    Node* left;
    Node* right;
    
    Node(int val) {
        data = val;
        left = nullptr;
        right = nullptr;
    }
};

// Create a binary tree
Node* root = new Node(10);
root->left = new Node(5);
root->right = new Node(15);
root->left->left = new Node(3);
root->left->right = new Node(7);
                </div>
                
                <strong>🔄 Tree Traversal Methods:</strong><br>
                <strong>Inorder (Left-Root-Right):</strong> 3, 5, 7, 10, 12, 15, 20<br>
                <strong>Preorder (Root-Left-Right):</strong> 10, 5, 3, 7, 15, 12, 20<br>
                <strong>Postorder (Left-Right-Root):</strong> 3, 7, 5, 12, 20, 15, 10<br>
            """,
            'image_type': None,
            'image_data': None
        }
    
    # Sorting Algorithms Comparison
    elif 'sorting algorithm' in question_lower or 'complexity' in question_lower:
        return {
            'text': """
                <strong>📈 Sorting Algorithms Comparison Chart</strong><br><br>
                
                <div class='algorithm-visual'>
                    <strong>⏱️ Time & Space Complexity Comparison:</strong><br><br>
                    <table style='width: 100%; border-collapse: collapse;'>
                        <tr style='background: #667eea; color: white;'>
                            <th style='padding: 10px; border: 1px solid #ddd;'>Algorithm</th>
                            <th style='padding: 10px; border: 1px solid #ddd;'>Best</th>
                            <th style='padding: 10px; border: 1px solid #ddd;'>Average</th>
                            <th style='padding: 10px; border: 1px solid #ddd;'>Worst</th>
                            <th style='padding: 10px; border: 1px solid #ddd;'>Space</th>
                        </tr>
                        <tr>
                            <td style='padding: 8px; border: 1px solid #ddd;'>Quick Sort</td>
                            <td style='padding: 8px; border: 1px solid #ddd;'>O(n log n)</td>
                            <td style='padding: 8px; border: 1px solid #ddd;'>O(n log n)</td>
                            <td style='padding: 8px; border: 1px solid #ddd;'>O(n²)</td>
                            <td style='padding: 8px; border: 1px solid #ddd;'>O(log n)</td>
                        </tr>
                        <tr style='background: #f0f0f0;'>
                            <td style='padding: 8px; border: 1px solid #ddd;'>Merge Sort</td>
                            <td style='padding: 8px; border: 1px solid #ddd;'>O(n log n)</td>
                            <td style='padding: 8px; border: 1px solid #ddd;'>O(n log n)</td>
                            <td style='padding: 8px; border: 1px solid #ddd;'>O(n log n)</td>
                            <td style='padding: 8px; border: 1px solid #ddd;'>O(n)</td>
                        </tr>
                        <tr>
                            <td style='padding: 8px; border: 1px solid #ddd;'><strong>Heap Sort</strong></td>
                            <td style='padding: 8px; border: 1px solid #ddd;'><strong>O(n log n)</strong></td>
                            <td style='padding: 8px; border: 1px solid #ddd;'><strong>O(n log n)</strong></td>
                            <td style='padding: 8px; border: 1px solid #ddd;'><strong>O(n log n)</strong></td>
                            <td style='padding: 8px; border: 1px solid #ddd;'><strong>O(1)</strong></td>
                        </tr>
                        <tr style='background: #f0f0f0;'>
                            <td style='padding: 8px; border: 1px solid #ddd;'>Bubble Sort</td>
                            <td style='padding: 8px; border: 1px solid #ddd;'>O(n)</td>
                            <td style='padding: 8px; border: 1px solid #ddd;'>O(n²)</td>
                            <td style='padding: 8px; border: 1px solid #ddd;'>O(n²)</td>
                            <td style='padding: 8px; border: 1px solid #ddd;'>O(1)</td>
                        </tr>
                        <tr>
                            <td style='padding: 8px; border: 1px solid #ddd;'>Insertion Sort</td>
                            <td style='padding: 8px; border: 1px solid #ddd;'>O(n)</td>
                            <td style='padding: 8px; border: 1px solid #ddd;'>O(n²)</td>
                            <td style='padding: 8px; border: 1px solid #ddd;'>O(n²)</td>
                            <td style='padding: 8px; border: 1px solid #ddd;'>O(1)</td>
                        </tr>
                    </table>
                </div>
                
                <div class='algorithm-visual' style='margin-top: 15px;'>
                    <strong>📊 Visual Performance Chart:</strong><br><br>
                    <div style='background: #f0f0f0; padding: 10px; border-radius: 5px;'>
                        <div style='margin: 5px 0;'>
                            <span style='display: inline-block; width: 120px;'>O(n²) - Slow:</span>
                            <div style='display: inline-block; width: 80%; background: #ef4444; height: 20px; border-radius: 10px;'></div>
                        </div>
                        <div style='margin: 5px 0;'>
                            <span style='display: inline-block; width: 120px;'>O(n log n) - Fast:</span>
                            <div style='display: inline-block; width: 40%; background: #48bb78; height: 20px; border-radius: 10px;'></div>
                        </div>
                        <div style='margin: 5px 0;'>
                            <span style='display: inline-block; width: 120px;'>O(n) - Linear:</span>
                            <div style='display: inline-block; width: 20%; background: #4299e1; height: 20px; border-radius: 10px;'></div>
                        </div>
                        <div style='margin: 5px 0;'>
                            <span style='display: inline-block; width: 120px;'>O(log n) - Logarithmic:</span>
                            <div style='display: inline-block; width: 10%; background: #ed8936; height: 20px; border-radius: 10px;'></div>
                        </div>
                    </div>
                </div>
                
                <strong>🏆 Which to Choose?</strong><br>
                • <strong>Heap Sort:</strong> When you need guaranteed O(n log n) and O(1) space<br>
                • <strong>Quick Sort:</strong> For average-case speed (most practical)<br>
                • <strong>Merge Sort:</strong> For stable sorting with linked lists<br>
                • <strong>Bubble/Insertion:</strong> For small arrays (< 50 elements)<br>
            """,
            'image_type': None,
            'image_data': None
        }
    
    # Quick Sort Visual
    elif 'quick sort' in question_lower:
        return {
            'text': """
                <strong>⚡ Quick Sort - Visual Guide</strong><br><br>
                
                <strong>How Quick Sort Works (Simple):</strong><br>
                1. Pick a <strong>pivot</strong> element<br>
                2. Partition: Move smaller elements left, larger right<br>
                3. Recursively sort left and right subarrays<br><br>
                
                <div class='algorithm-visual'>
                    <strong>🔄 Step-by-Step Visualization:</strong><br><br>
                    Array: [8, 3, 9, 1, 5, 7, 2, 6]<br><br>
                    
                    <strong>Step 1:</strong> Choose pivot = 6<br>
                    [3, 1, 2, 5] <strong>6</strong> [8, 9, 7]<br><br>
                    
                    <strong>Step 2:</strong> Sort left: pivot = 5<br>
                    [1, 2] <strong>3</strong> [5] <strong>6</strong> [8, 9, 7]<br><br>
                    
                    <strong>Step 3:</strong> Sort right: pivot = 7<br>
                    [1, 2, 3, 5] <strong>6</strong> [7] <strong>8</strong> [9]<br><br>
                    
                    <strong>Final:</strong> [1, 2, 3, 5, 6, 7, 8, 9] ✅<br>
                </div>
                
                <strong>💻 C++ Code:</strong>
                <div class='code-block'>
int partition(int arr[], int low, int high) {
    int pivot = arr[high];
    int i = low - 1;
    
    for (int j = low; j < high; j++) {
        if (arr[j] <= pivot) {
            i++;
            swap(arr[i], arr[j]);
        }
    }
    swap(arr[i + 1], arr[high]);
    return i + 1;
}

void quickSort(int arr[], int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quickSort(arr, low, pi - 1);
        quickSort(arr, pi + 1, high);
    }
}
                </div>
            """,
            'image_type': None,
            'image_data': None
        }
    
    # Default response for other questions
    else:
        # Try to get answer from Ollama first
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "mistral",
                    "prompt": f"Provide a clear, detailed answer with examples and code if relevant: {question}",
                    "stream": False,
                    "options": {"temperature": 0.7}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                answer = response.json().get('response', '')
                return {
                    'text': answer.replace('\n', '<br>'),
                    'image_type': None,
                    'image_data': None
                }
        except:
            pass
        
        # Fallback response
        return {
            'text': """
                <strong>🤔 I can help you with various topics!</strong><br><br>
                
                Try asking me about:<br>
                • <strong>📊 Heap Sort</strong> - With visualization and C++ code<br>
                • <strong>🌳 Binary Trees</strong> - With diagrams and traversal<br>
                • <strong>📈 Sorting Algorithms</strong> - Complexity comparison chart<br>
                • <strong>⚡ Quick Sort</strong> - Step-by-step visualization<br>
                • <strong>🔍 Binary Search</strong> - Flowchart and implementation<br><br>
                
                <strong>Example questions you can ask:</strong><br>
                "Show me heap sort visualization"<br>
                "Draw a binary tree diagram"<br>
                "Compare sorting algorithm complexities"<br>
                "Explain quick sort with example"<br>
            """,
            'image_type': None,
            'image_data': None
        }

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get answer (with potential images)
        result = get_answer_with_image(user_message)
        
        return jsonify({
            'response': result['text'],
            'image_type': result['image_type'],
            'image_data': result['image_data']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎨 AI VISUAL ASSISTANT - Answers with Images & Diagrams")
    print("="*60)
    print("\n🚀 Server running at: http://localhost:5000")
    print("📱 Open this URL in your browser")
    print("\n💡 Features:")
    print("   • Visual diagrams for algorithms")
    print("   • C++ code with explanations")
    print("   • Complexity comparison charts")
    print("   • Tree and graph visualizations")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=False, host='127.0.0.1', port=5000)