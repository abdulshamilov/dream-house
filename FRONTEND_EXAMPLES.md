# 💻 Frontend Examples - Примеры кода для интеграции AI

## 🎨 Vue.js пример (самый простой)

```vue
<template>
  <div class="chat-container">
    <!-- История сообщений -->
    <div class="messages">
      <div v-for="msg in history" :key="msg.id" class="message-group">
        <div class="user-message">
          <strong>Вы:</strong> {{ msg.message }}
        </div>
        <div class="ai-message">
          <strong>AI:</strong> {{ msg.response }}
        </div>
        <div class="cards-list" v-if="msg.referenced_cards.length > 0">
          <small>Упомянуты карточки: {{ msg.referenced_cards.join(', ') }}</small>
        </div>
        <div class="rating">
          <button 
            @click="rateMessage(msg.id, true)"
            :class="{ active: msg.is_helpful === true }"
          >👍 Полезно</button>
          <button 
            @click="rateMessage(msg.id, false)"
            :class="{ active: msg.is_helpful === false }"
          >👎 Не полезно</button>
        </div>
      </div>
    </div>

    <!-- Форма отправки -->
    <div class="input-area">
      <textarea 
        v-model="message"
        placeholder="Напишите, что вы ищете..."
        @keyup.enter="sendMessage"
      ></textarea>
      
      <div class="preferences">
        <input v-model.number="prefs.city" type="number" placeholder="Город (ID)">
        <input v-model.number="prefs.rooms" type="number" placeholder="Комнаты">
        <input v-model.number="prefs.price_max" type="number" placeholder="Макс цена">
      </div>
      
      <button @click="sendMessage" :disabled="loading">
        {{ loading ? 'Загрузка...' : 'Отправить' }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      message: '',
      history: [],
      loading: false,
      token: localStorage.getItem('token'),
      prefs: {
        city: null,
        rooms: null,
        price_max: null
      }
    }
  },
  
  mounted() {
    this.loadHistory();
  },
  
  methods: {
    async loadHistory() {
      const response = await fetch('http://localhost:8000/api/cards/ai/history/', {
        headers: {
          'Authorization': `Bearer ${this.token}`
        }
      });
      const data = await response.json();
      this.history = data.results || [];
    },
    
    async sendMessage() {
      if (!this.message.trim()) return;
      
      this.loading = true;
      
      // Фильтруем пустые значения
      const preferences = {};
      Object.keys(this.prefs).forEach(key => {
        if (this.prefs[key]) preferences[key] = this.prefs[key];
      });
      
      try {
        const response = await fetch('http://localhost:8000/api/cards/ai/chat/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message: this.message,
            user_preferences: preferences
          })
        });
        
        const data = await response.json();
        this.history.push(data);
        this.message = '';
      } catch (error) {
        alert('Ошибка: ' + error.message);
      } finally {
        this.loading = false;
      }
    },
    
    async rateMessage(messageId, isHelpful) {
      await fetch(`http://localhost:8000/api/cards/ai/chat/${messageId}/rate/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_helpful: isHelpful })
      });
      
      // Обновить историю
      this.loadHistory();
    }
  }
}
</script>

<style scoped>
.chat-container {
  max-width: 800px;
  margin: 0 auto;
}

.messages {
  height: 500px;
  overflow-y: auto;
  margin-bottom: 20px;
  border: 1px solid #ddd;
  padding: 20px;
  border-radius: 8px;
}

.message-group {
  margin-bottom: 20px;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 4px;
}

.user-message {
  color: #0066cc;
  margin-bottom: 8px;
}

.ai-message {
  color: #333;
  margin-bottom: 8px;
}

.cards-list {
  color: #666;
  font-size: 12px;
  margin: 8px 0;
}

.rating button {
  margin: 5px 5px 5px 0;
  padding: 5px 10px;
  background: #eee;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.rating button.active {
  background: #0066cc;
  color: white;
}

.input-area textarea {
  width: 100%;
  height: 80px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: Arial;
}

.preferences {
  display: flex;
  gap: 10px;
  margin: 10px 0;
}

.preferences input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  padding: 10px 20px;
  background: #0066cc;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

button:disabled {
  background: #999;
  cursor: not-allowed;
}
</style>
```

---

## ⚛️ React пример

```jsx
import React, { useState, useEffect } from 'react';

function AIChatApp() {
  const [message, setMessage] = useState('');
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [prefs, setPrefs] = useState({
    city: '',
    rooms: '',
    price_max: ''
  });
  
  const token = localStorage.getItem('token');
  
  useEffect(() => {
    loadHistory();
  }, []);
  
  const loadHistory = async () => {
    const response = await fetch('http://localhost:8000/api/cards/ai/history/', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setHistory(data.results || []);
  };
  
  const sendMessage = async () => {
    if (!message.trim()) return;
    
    setLoading(true);
    
    const preferences = {};
    Object.entries(prefs).forEach(([key, value]) => {
      if (value) preferences[key] = isNaN(value) ? value : parseInt(value);
    });
    
    try {
      const response = await fetch('http://localhost:8000/api/cards/ai/chat/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message,
          user_preferences: preferences
        })
      });
      
      const data = await response.json();
      setHistory([...history, data]);
      setMessage('');
    } catch (error) {
      alert('Ошибка: ' + error.message);
    } finally {
      setLoading(false);
    }
  };
  
  const rateMessage = async (messageId, isHelpful) => {
    await fetch(`http://localhost:8000/api/cards/ai/chat/${messageId}/rate/`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ is_helpful: isHelpful })
    });
    
    loadHistory();
  };
  
  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <h1>💬 AI Помощник</h1>
      
      <div style={{ 
        height: '500px', 
        overflow: 'auto', 
        border: '1px solid #ddd',
        padding: '20px',
        marginBottom: '20px'
      }}>
        {history.map(msg => (
          <div key={msg.id} style={{ 
            marginBottom: '20px', 
            padding: '10px',
            backgroundColor: '#f9f9f9',
            borderRadius: '4px'
          }}>
            <div style={{ color: '#0066cc', marginBottom: '8px' }}>
              <strong>Вы:</strong> {msg.message}
            </div>
            <div style={{ marginBottom: '8px' }}>
              <strong>AI:</strong> {msg.response}
            </div>
            {msg.referenced_cards.length > 0 && (
              <div style={{ fontSize: '12px', color: '#666' }}>
                Карточки: {msg.referenced_cards.join(', ')}
              </div>
            )}
            <div style={{ marginTop: '8px' }}>
              <button 
                onClick={() => rateMessage(msg.id, true)}
                style={{ 
                  marginRight: '5px',
                  background: msg.is_helpful === true ? '#0066cc' : '#eee',
                  color: msg.is_helpful === true ? 'white' : '#333'
                }}
              >👍</button>
              <button 
                onClick={() => rateMessage(msg.id, false)}
                style={{ 
                  background: msg.is_helpful === false ? '#0066cc' : '#eee',
                  color: msg.is_helpful === false ? 'white' : '#333'
                }}
              >👎</button>
            </div>
          </div>
        ))}
      </div>
      
      <textarea 
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Напишите запрос..."
        style={{ 
          width: '100%', 
          height: '80px',
          padding: '10px',
          marginBottom: '10px'
        }}
      />
      
      <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
        <input 
          type="number"
          placeholder="Город (ID)"
          value={prefs.city}
          onChange={(e) => setPrefs({...prefs, city: e.target.value})}
          style={{ flex: 1, padding: '8px' }}
        />
        <input 
          type="number"
          placeholder="Комнаты"
          value={prefs.rooms}
          onChange={(e) => setPrefs({...prefs, rooms: e.target.value})}
          style={{ flex: 1, padding: '8px' }}
        />
        <input 
          type="number"
          placeholder="Макс цена"
          value={prefs.price_max}
          onChange={(e) => setPrefs({...prefs, price_max: e.target.value})}
          style={{ flex: 1, padding: '8px' }}
        />
      </div>
      
      <button 
        onClick={sendMessage}
        disabled={loading}
        style={{ 
          width: '100%', 
          padding: '10px',
          background: loading ? '#999' : '#0066cc'
        }}
      >
        {loading ? 'Загрузка...' : 'Отправить'}
      </button>
    </div>
  );
}

export default AIChatApp;
```

---

## 🎯 Vanilla JavaScript (без фреймворков)

```html
<!DOCTYPE html>
<html>
<head>
  <title>AI Chat</title>
  <style>
    body { font-family: Arial; max-width: 800px; margin: 0 auto; }
    .messages { 
      height: 500px; 
      overflow-y: auto; 
      border: 1px solid #ddd; 
      padding: 20px; 
      margin-bottom: 20px;
    }
    .message { 
      margin-bottom: 20px; 
      padding: 10px; 
      background: #f9f9f9;
    }
    textarea { width: 100%; height: 80px; margin-bottom: 10px; }
    input { padding: 8px; margin-right: 5px; }
    button { padding: 10px 20px; background: #0066cc; color: white; border: none; }
  </style>
</head>
<body>
  <h1>💬 AI Помощник</h1>
  
  <div id="messages" class="messages"></div>
  
  <textarea id="message" placeholder="Напишите запрос..."></textarea>
  
  <div>
    <input type="number" id="city" placeholder="Город (ID)">
    <input type="number" id="rooms" placeholder="Комнаты">
    <input type="number" id="price_max" placeholder="Макс цена">
  </div>
  
  <button onclick="sendMessage()" id="btn">Отправить</button>

  <script>
    const token = localStorage.getItem('token');
    
    async function loadHistory() {
      const resp = await fetch('http://localhost:8000/api/cards/ai/history/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await resp.json();
      const container = document.getElementById('messages');
      container.innerHTML = '';
      
      data.results?.forEach(msg => {
        const div = document.createElement('div');
        div.className = 'message';
        div.innerHTML = `
          <strong>Вы:</strong> ${msg.message}<br>
          <strong>AI:</strong> ${msg.response}<br>
          <small>Карточки: ${msg.referenced_cards.join(', ')}</small><br>
          <button onclick="rate(${msg.id}, true)">👍</button>
          <button onclick="rate(${msg.id}, false)">👎</button>
        `;
        container.appendChild(div);
      });
    }
    
    async function sendMessage() {
      const message = document.getElementById('message').value;
      const btn = document.getElementById('btn');
      
      if (!message.trim()) return;
      
      btn.disabled = true;
      
      const prefs = {
        city: parseInt(document.getElementById('city').value) || undefined,
        rooms: parseInt(document.getElementById('rooms').value) || undefined,
        price_max: parseInt(document.getElementById('price_max').value) || undefined
      };
      
      // Удалить undefined значения
      Object.keys(prefs).forEach(k => prefs[k] === undefined && delete prefs[k]);
      
      try {
        const resp = await fetch('http://localhost:8000/api/cards/ai/chat/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message,
            user_preferences: prefs
          })
        });
        
        const data = await resp.json();
        document.getElementById('message').value = '';
        loadHistory();
      } catch (error) {
        alert('Ошибка: ' + error.message);
      } finally {
        btn.disabled = false;
      }
    }
    
    async function rate(messageId, isHelpful) {
      await fetch(`http://localhost:8000/api/cards/ai/chat/${messageId}/rate/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_helpful: isHelpful })
      });
      loadHistory();
    }
    
    // Загрузить историю при открытии
    loadHistory();
  </script>
</body>
</html>
```

---

## 🐍 Python CLI пример

```python
#!/usr/bin/env python3
import requests
import json
import sys

TOKEN = "your_token_here"
BASE_URL = "http://localhost:8000/api"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def chat(message, city=None, rooms=None, price_max=None):
    """Отправить сообщение AI"""
    
    prefs = {}
    if city: prefs['city'] = city
    if rooms: prefs['rooms'] = rooms
    if price_max: prefs['price_max'] = price_max
    
    resp = requests.post(
        f"{BASE_URL}/cards/ai/chat/",
        headers=headers,
        json={
            "message": message,
            "user_preferences": prefs
        }
    )
    
    data = resp.json()
    if resp.status_code == 201:
        print(f"\n🤖 AI: {data['response']}")
        print(f"📌 Карточки: {data['referenced_cards']}")
        print(f"📊 Токены: {data['tokens_used']}")
        return data['id']
    else:
        print(f"❌ Ошибка: {data}")
        return None

def history():
    """Получить историю"""
    resp = requests.get(f"{BASE_URL}/cards/ai/history/", headers=headers)
    data = resp.json()
    
    for msg in data.get('results', []):
        print(f"\n👤 Вы: {msg['message']}")
        print(f"🤖 AI: {msg['response']}")
        print(f"👍 Полезно: {msg['is_helpful']}")

def rate(message_id, helpful):
    """Оценить сообщение"""
    resp = requests.patch(
        f"{BASE_URL}/cards/ai/chat/{message_id}/rate/",
        headers=headers,
        json={"is_helpful": helpful}
    )
    print(f"✅ Оценка {'успешна' if resp.status_code == 200 else 'ошибка'}")

def recommendations():
    """Получить рекомендации"""
    resp = requests.get(f"{BASE_URL}/cards/recommendations/", headers=headers)
    data = resp.json()
    
    for rec in data.get('results', []):
        print(f"\n📍 {rec['card']['title']}")
        print(f"   Цена: {rec['card']['price']}")
        print(f"   Оценка: {rec['score']:.2f}")
        print(f"   Причина: {rec['reason']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python ai.py chat '<сообщение>' [--city 1] [--rooms 3] [--price 3000000]")
        print("  python ai.py history")
        print("  python ai.py rate <id> <true|false>")
        print("  python ai.py recommendations")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "chat" and len(sys.argv) > 2:
        message = sys.argv[2]
        city = rooms = price_max = None
        
        for i in range(3, len(sys.argv), 2):
            if sys.argv[i] == "--city" and i+1 < len(sys.argv):
                city = int(sys.argv[i+1])
            elif sys.argv[i] == "--rooms" and i+1 < len(sys.argv):
                rooms = int(sys.argv[i+1])
            elif sys.argv[i] == "--price" and i+1 < len(sys.argv):
                price_max = int(sys.argv[i+1])
        
        chat(message, city, rooms, price_max)
    
    elif command == "history":
        history()
    
    elif command == "rate" and len(sys.argv) > 3:
        message_id = int(sys.argv[2])
        helpful = sys.argv[3].lower() == "true"
        rate(message_id, helpful)
    
    elif command == "recommendations":
        recommendations()
    
    else:
        print("❌ Неизвестная команда или недостаточно аргументов")
```

---

## 📱 Использование

### Vue
```bash
npm install axios
```

### React
```bash
npx create-react-app ai-chat
cd ai-chat
npm start
```

### Vanilla JS
Просто откройте HTML файл в браузере

### Python
```bash
pip install requests
python ai.py chat "Найди квартиру" --city 1 --rooms 3 --price 3000000
```

---

**Всё готово для интеграции!** 🚀
