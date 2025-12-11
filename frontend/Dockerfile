
FROM node:20-alpine

WORKDIR /app

COPY package.json ./

# npm registry 인증 제거
RUN npm config delete //registry.npmjs.org/:_authToken || true
RUN npm config set registry https://registry.npmjs.org/

RUN npm install

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
# npm registry 인증 제거 → 토큰 만료 문제 방지
RUN npm config delete //registry.npmjs.org/:_authToken || true
RUN npm config set registry https://registry.npmjs.org/
