@echo off
REM Local Testing Script for Brain OS Phase 3
REM This script starts Neo4j and BrainOS for local testing

echo ========================================
echo Brain OS Phase 3 Local Testing
echo ========================================
echo.

echo [1/3] Checking Neo4j...
docker ps --filter "name=neo4j" --format "{{.Names}}" | findstr "neo4j" >nul
if errorlevel 1 (
    echo Starting Neo4j container...
    docker run -d --name neo4j-test ^
        -p 7687:7687 ^
        -p 7474:7474 ^
        -e NEO4J_AUTH=neo4j/brainos_password_123 ^
        neo4j:5.25-community
    echo Waiting for Neo4j to start...
    timeout /t 10 /nobreak >nul
) else (
    echo Neo4j already running
)
echo.

echo [2/3] Starting BrainOS server...
docker compose -f docker-compose-test.yml up --build -d
echo Waiting for server to start...
timeout /t 5 /nobreak >nul
echo.

echo [3/3] Running Phase 3 tests...
uv run python test_phase3.py
echo.

echo ========================================
echo Testing complete!
echo ========================================
echo.
echo To clean up:
echo   docker compose -f docker-compose-test.yml down
echo   docker stop neo4j-test ^&^& docker rm neo4j-test
echo.
