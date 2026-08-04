const express = require('express');
const app = express();
const port = process.env.PORT || 3001;

app.get('/', (req, res) => {
  res.send('Xin chào! Server đã chạy thành công');
});

app.listen(port, () => {
  console.log(`Server đang chạy tại http://localhost:${port}`);
});
