// src/components/CategoryManagement.jsx
import React, { useState, useEffect } from 'react';
import axios from '../api/axiosConfig';

function CategoryManagement() {
  const [categories, setCategories] = useState([]);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [editingCategory, setEditingCategory] = useState(null);
  const [editingCategoryName, setEditingCategoryName] = useState('');

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await axios.get('/obtenerCategorias');
      setCategories(response.data);
    } catch (error) {
      console.error('Error al obtener las categorías:', error);
    }
  };

  const handleAddCategory = async () => {
    if (!newCategoryName.trim()) return;
    try {
      await axios.post(`/categoria/${newCategoryName}`);
      setNewCategoryName('');
      fetchCategories();
    } catch (error) {
      console.error('Error al agregar la categoría:', error);
    }
  };

  const handleUpdateCategory = async (id) => {
    if (!editingCategoryName.trim()) return;
    try {
      await axios.put(`/editarCategoria/${id}`, { nombre: editingCategoryName });
      setEditingCategory(null);
      setEditingCategoryName('');
      fetchCategories();
    } catch (error) {
      console.error('Error al actualizar la categoría:', error);
    }
  };

  const handleDeleteCategory = async (id) => {
    try {
      await axios.delete(`/eliminarCategoria/${id}`);
      fetchCategories();
    } catch (error) {
      console.error('Error al eliminar la categoría:', error);
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold text-white mb-4">Gestión de Categorías</h2>
      <div className="mb-6">
        <input
          type="text"
          value={newCategoryName}
          onChange={(e) => setNewCategoryName(e.target.value)}
          placeholder="Nueva categoría"
          className="px-4 py-2 rounded-md bg-gray-800 text-gray-200 mr-2"
        />
        <button
          onClick={handleAddCategory}
          className="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-md"
        >
          Agregar
        </button>
      </div>
      <ul>
        {categories.map((category) => (
          <li key={category.id} className="flex items-center mb-2">
            {editingCategory === category.id ? (
              <>
                <input
                  type="text"
                  value={editingCategoryName}
                  onChange={(e) => setEditingCategoryName(e.target.value)}
                  className="px-4 py-2 rounded-md bg-gray-800 text-gray-200 mr-2"
                />
                <button
                  onClick={() => handleUpdateCategory(category.id)}
                  className="bg-blue-600 hover:bg-blue-700 text-white py-1 px-3 rounded-md mr-2"
                >
                  Guardar
                </button>
                <button
                  onClick={() => setEditingCategory(null)}
                  className="bg-red-600 hover:bg-red-700 text-white py-1 px-3 rounded-md"
                >
                  Cancelar
                </button>
              </>
            ) : (
              <>
                <span className="text-gray-200 mr-2">{category.nombre}</span>
                <button
                  onClick={() => {
                    setEditingCategory(category.id);
                    setEditingCategoryName(category.nombre);
                  }}
                  className="bg-blue-600 hover:bg-blue-700 text-white py-1 px-3 rounded-md mr-2"
                >
                  Editar
                </button>
                <button
                  onClick={() => handleDeleteCategory(category.id)}
                  className="bg-red-600 hover:bg-red-700 text-white py-1 px-3 rounded-md"
                >
                  Eliminar
                </button>
              </>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default CategoryManagement;
