using DotNetCoreSqlDb.Models;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

builder.Logging.AddAzureWebAppDiagnostics();

// Add services to the container.
builder.Services.AddControllersWithViews();

// 1. ИСПРАВЛЕНИЕ: Жестко указываем использовать SQL Server и нашу строку подключения из Docker
builder.Services.AddDbContext<MyDatabaseContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("MyDbConnection")));

var app = builder.Build();

// 2. ДОБАВЛЕНИЕ: Автоматически применяем миграции (создаем таблицы в БД) при старте контейнера
using (var scope = app.Services.CreateScope())
{
    var services = scope.ServiceProvider;
    try
    {
        var context = services.GetRequiredService<MyDatabaseContext>();
        context.Database.EnsureCreated();
    }
    catch (Exception ex)
    {
        var logger = services.GetRequiredService<ILogger<Program>>();
        logger.LogError(ex, "Произошла ошибка при миграции базы данных.");
    }
}

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}
else {
    app.UseExceptionHandler("/Error");
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

// app.UseHttpsRedirection();
app.UseStaticFiles();

app.UseRouting();

app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Todos}/{action=Index}/{id?}");

app.Run();