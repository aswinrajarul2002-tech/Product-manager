from flask import Flask, jsonify, request, abort, render_template_string

app = Flask(__name__)

# ==============================================================================
# In-Memory Database Simulation
# ==============================================================================
products_db = {
    1: {"id": 1, "name": "Laptop", "category": "Electronics", "price": 999.99, "in_stock": True},
    2: {"id": 2, "name": "Coffee Maker", "category": "Appliances", "price": 49.99, "in_stock": True},
    3: {"id": 3, "name": "Wireless Mouse", "category": "Electronics", "price": 25.50, "in_stock": False}
}
next_id = 4

# ==============================================================================
# Single-Page UI Dashboard (HTML + CSS + Vanilla JS)
# ==============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Management Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen p-6 font-sans">
    <div class="max-w-5xl mx-auto">
        <header class="mb-8 flex justify-between items-center bg-white p-6 rounded-lg shadow-sm">
            <div>
                <h1 class="text-2xl font-bold text-gray-800">Product Manager</h1>
                <p class="text-sm text-gray-500">Real-time REST API Web Interface</p>
            </div>
            <span class="bg-green-100 text-green-800 text-xs font-semibold px-3 py-1 rounded-full">Server Active</span>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- Form Section -->
            <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200 h-fit">
                <h2 id="form-title" class="text-lg font-semibold mb-4 text-gray-700">Add New Product</h2>
                <form id="product-form" class="space-y-4">
                    <input type="hidden" id="product-id">
                    
                    <div>
                        <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Product Name</label>
                        <input type="text" id="name" required class="w-full border rounded p-2 text-sm focus:outline-blue-500">
                    </div>

                    <div>
                        <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Category</label>
                        <input type="text" id="category" required class="w-full border rounded p-2 text-sm focus:outline-blue-500">
                    </div>

                    <div>
                        <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Price ($)</label>
                        <input type="number" step="0.01" id="price" required class="w-full border rounded p-2 text-sm focus:outline-blue-500">
                    </div>

                    <div class="flex items-center gap-2">
                        <input type="checkbox" id="in_stock" checked class="w-4 h-4 text-blue-600 rounded">
                        <label for="in_stock" class="text-sm text-gray-700">Available in Stock</label>
                    </div>

                    <div class="flex gap-2 pt-2">
                        <button type="submit" id="submit-btn" class="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded text-sm transition">Add Product</button>
                        <button type="button" id="cancel-btn" onclick="resetForm()" class="hidden bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium px-4 py-2 rounded text-sm transition">Cancel</button>
                    </div>
                </form>
            </div>

            <!-- Table Section -->
            <div class="md:col-span-2 bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-lg font-semibold text-gray-700">Inventory Directory</h2>
                    <button onclick="fetchProducts()" class="text-xs text-blue-600 hover:underline">Refresh Data</button>
                </div>
                
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-sm">
                        <thead>
                            <tr class="border-b bg-gray-50 text-gray-600 uppercase text-xs">
                                <th class="p-3">ID</th>
                                <th class="p-3">Name</th>
                                <th class="p-3">Category</th>
                                <th class="p-3">Price</th>
                                <th class="p-3">Stock</th>
                                <th class="p-3 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody id="product-table-body">
                            <!-- JS populate rows -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_URL = '/api/products';

        document.addEventListener('DOMContentLoaded', fetchProducts);

        // GET: Load all products
        async function fetchProducts() {
            try {
                const res = await fetch(API_URL);
                const products = await res.json();
                const tbody = document.getElementById('product-table-body');
                tbody.innerHTML = '';

                products.forEach(p => {
                    tbody.innerHTML += `
                        <tr class="border-b hover:bg-gray-50">
                            <td class="p-3 font-mono text-gray-500">#${p.id}</td>
                            <td class="p-3 font-semibold text-gray-800">${p.name}</td>
                            <td class="p-3 text-gray-600">${p.category}</td>
                            <td class="p-3 font-mono">$${parseFloat(p.price).toFixed(2)}</td>
                            <td class="p-3">
                                <span class="px-2 py-0.5 text-xs rounded-full ${p.in_stock ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}">
                                    ${p.in_stock ? 'In Stock' : 'Out of Stock'}
                                </span>
                            </td>
                            <td class="p-3 text-right space-x-2">
                                <button onclick='editProduct(${JSON.stringify(p)})' class="text-blue-600 hover:text-blue-800 font-medium">Edit</button>
                                <button onclick="deleteProduct(${p.id})" class="text-red-600 hover:text-red-800 font-medium">Delete</button>
                            </td>
                        </tr>
                    `;
                });
            } catch (err) {
                console.error("Error fetching inventory:", err);
            }
        }

        // POST & PUT: Handle Form Submission
        document.getElementById('product-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('product-id').value;
            const payload = {
                name: document.getElementById('name').value,
                category: document.getElementById('category').value,
                price: parseFloat(document.getElementById('price').value),
                in_stock: document.getElementById('in_stock').checked
            };

            const url = id ? `${API_URL}/${id}` : API_URL;
            const method = id ? 'PUT' : 'POST';

            const res = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                resetForm();
                fetchProducts();
            } else {
                const errorData = await res.json();
                alert(`Error: ${errorData.message}`);
            }
        });

        // Populate form fields for updating
        function editProduct(p) {
            document.getElementById('product-id').value = p.id;
            document.getElementById('name').value = p.name;
            document.getElementById('category').value = p.category;
            document.getElementById('price').value = p.price;
            document.getElementById('in_stock').checked = p.in_stock;

            document.getElementById('form-title').innerText = `Edit Product #${p.id}`;
            document.getElementById('submit-btn').innerText = 'Update Product';
            document.getElementById('submit-btn').className = 'flex-1 bg-yellow-600 hover:bg-yellow-700 text-white font-medium py-2 rounded text-sm transition';
            document.getElementById('cancel-btn').classList.remove('hidden');
        }

        // Reset form state
        function resetForm() {
            document.getElementById('product-id').value = '';
            document.getElementById('product-form').reset();
            document.getElementById('in_stock').checked = true;

            document.getElementById('form-title').innerText = 'Add New Product';
            document.getElementById('submit-btn').innerText = 'Add Product';
            document.getElementById('submit-btn').className = 'flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded text-sm transition';
            document.getElementById('cancel-btn').classList.add('hidden');
        }

        // DELETE: Purge Product Record
        async function deleteProduct(id) {
            if (!confirm(`Are you sure you want to delete product #${id}?`)) return;

            const res = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
            if (res.ok) {
                fetchProducts();
            } else {
                alert("Failed to delete product record.");
            }
        }
    </script>
</body>
</html>
"""

# ==============================================================================
# Web & API Routing Layer
# ==============================================================================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(list(products_db.values())), 200

@app.route('/api/products', methods=['POST'])
def create_product():
    global next_id
    data = request.get_json(silent=True)
    if not data or not all(k in data for k in ('name', 'category', 'price')):
        abort(400, description="Invalid payload. 'name', 'category', and 'price' are required.")

    new_product = {
        "id": next_id,
        "name": str(data['name']).strip(),
        "category": str(data['category']).strip(),
        "price": float(data['price']),
        "in_stock": bool(data.get('in_stock', True))
    }
    products_db[next_id] = new_product
    next_id += 1
    return jsonify(new_product), 201

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = products_db.get(product_id)
    if not product:
        abort(404, description="Product not found.")

    data = request.get_json(silent=True) or {}
    if 'name' in data: product['name'] = str(data['name']).strip()
    if 'category' in data: product['category'] = str(data['category']).strip()
    if 'price' in data: product['price'] = float(data['price'])
    if 'in_stock' in data: product['in_stock'] = bool(data['in_stock'])

    return jsonify(product), 200

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    if product_id not in products_db:
        abort(404, description="Product not found.")
    del products_db[product_id]
    return jsonify({"message": f"Product {product_id} deleted successfully."}), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=7000, debug=True)