// src/components/CategoryList.jsx
import React, { useEffect, useState } from 'react';
import axios from '../api/axiosConfig';

function CategoryList({ selectedCategory, setSelectedCategory }) {
  const [categories, setCategories] = useState([]);

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

  return (
    <div className="flex space-x-4 overflow-x-auto p-4 bg-gray-900">
      <button
        onClick={() => setSelectedCategory(null)}
        className={`px-4 py-2 rounded-full ${
          !selectedCategory ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300'
        }`}
      >
        Todas
      </button>
      {categories.map((category) => (
        <button
          key={category.id}
          onClick={() => setSelectedCategory(category.id)}
          className={`px-4 py-2 rounded-full ${
            selectedCategory === category.id ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300'
          }`}
        >
          {category.nombre}
        </button>
      ))}
    </div>
  );
}

export default CategoryList;
