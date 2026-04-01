# Используем образ с SDK для сборки и запуска
FROM mcr.microsoft.com/dotnet/sdk:6.0
WORKDIR /app

# Копируем все исходники в контейнер
COPY . .

# Восстанавливаем зависимости проекта
RUN dotnet restore

# Открываем порт и задаем переменную окружения для ASP.NET Core
EXPOSE 80
ENV ASPNETCORE_URLS=http://+:80

# Запускаем проект
CMD ["dotnet", "run"]