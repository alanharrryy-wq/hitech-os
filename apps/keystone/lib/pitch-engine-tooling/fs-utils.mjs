import fs from "node:fs"
import fsp from "node:fs/promises"
import path from "node:path"
import { stableJsonStringify } from "./deterministic.mjs"
import { assertPathInside } from "./windows-safe.mjs"

export async function ensureDir(targetPath) {
  await fsp.mkdir(targetPath, { recursive: true })
  return targetPath
}

export function ensureDirSync(targetPath) {
  fs.mkdirSync(targetPath, { recursive: true })
  return targetPath
}

export async function pathExists(targetPath) {
  try {
    await fsp.access(targetPath)
    return true
  } catch {
    return false
  }
}

export function pathExistsSync(targetPath) {
  try {
    fs.accessSync(targetPath)
    return true
  } catch {
    return false
  }
}

export async function readTextIfExists(targetPath) {
  if (!(await pathExists(targetPath))) {
    return null
  }
  return fsp.readFile(targetPath, "utf8")
}

export async function writeTextFile(targetPath, content) {
  await ensureDir(path.dirname(targetPath))
  await fsp.writeFile(targetPath, content, "utf8")
}

export function writeTextFileSync(targetPath, content) {
  ensureDirSync(path.dirname(targetPath))
  fs.writeFileSync(targetPath, content, "utf8")
}

export async function writeJsonFile(targetPath, value) {
  const payload = stableJsonStringify(value)
  await writeTextFile(targetPath, payload)
}

export function writeJsonFileSync(targetPath, value) {
  const payload = stableJsonStringify(value)
  writeTextFileSync(targetPath, payload)
}

export async function readJsonFile(targetPath) {
  const payload = await fsp.readFile(targetPath, "utf8")
  return JSON.parse(payload)
}

export async function readJsonIfExists(targetPath, fallback = null) {
  if (!(await pathExists(targetPath))) {
    return fallback
  }
  return readJsonFile(targetPath)
}

export function readJsonIfExistsSync(targetPath, fallback = null) {
  if (!pathExistsSync(targetPath)) {
    return fallback
  }

  const payload = fs.readFileSync(targetPath, "utf8")
  return JSON.parse(payload)
}

export async function appendText(targetPath, text) {
  await ensureDir(path.dirname(targetPath))
  await fsp.appendFile(targetPath, text, "utf8")
}

export async function listDirectories(parentPath) {
  if (!(await pathExists(parentPath))) {
    return []
  }

  const entries = await fsp.readdir(parentPath, {
    withFileTypes: true
  })

  return entries
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort((a, b) => a.localeCompare(b))
}

export async function listFilesRecursive(parentPath) {
  if (!(await pathExists(parentPath))) {
    return []
  }

  const results = []

  async function walk(currentPath) {
    const entries = await fsp.readdir(currentPath, {
      withFileTypes: true
    })

    for (const entry of entries) {
      const fullPath = path.join(currentPath, entry.name)
      if (entry.isDirectory()) {
        await walk(fullPath)
      } else if (entry.isFile()) {
        results.push(fullPath)
      }
    }
  }

  await walk(parentPath)
  return results.sort((a, b) => a.localeCompare(b))
}

export async function removeDirectory(targetPath) {
  if (!(await pathExists(targetPath))) {
    return false
  }

  await fsp.rm(targetPath, { recursive: true, force: true })
  return true
}

export async function copyFileSafe(sourcePath, targetPath) {
  await ensureDir(path.dirname(targetPath))
  await fsp.copyFile(sourcePath, targetPath)
}

export async function copyDirectoryRecursive(sourcePath, targetPath) {
  await ensureDir(targetPath)
  const entries = await fsp.readdir(sourcePath, {
    withFileTypes: true
  })

  for (const entry of entries) {
    const sourceEntry = path.join(sourcePath, entry.name)
    const targetEntry = path.join(targetPath, entry.name)

    if (entry.isDirectory()) {
      await copyDirectoryRecursive(sourceEntry, targetEntry)
    } else if (entry.isFile()) {
      await copyFileSafe(sourceEntry, targetEntry)
    }
  }
}

export async function statSafe(targetPath) {
  try {
    return await fsp.stat(targetPath)
  } catch {
    return null
  }
}

export function touchFileSync(targetPath, content = "") {
  ensureDirSync(path.dirname(targetPath))
  fs.writeFileSync(targetPath, content, "utf8")
}

export async function touchFile(targetPath, content = "") {
  await ensureDir(path.dirname(targetPath))
  await fsp.writeFile(targetPath, content, "utf8")
}

export function atomicWriteJsonSync(targetPath, value) {
  const tempPath = `${targetPath}.tmp`
  writeJsonFileSync(tempPath, value)
  fs.renameSync(tempPath, targetPath)
}

export async function atomicWriteJson(targetPath, value) {
  const tempPath = `${targetPath}.tmp`
  await writeJsonFile(tempPath, value)
  await fsp.rename(tempPath, targetPath)
}

export async function ensureWritableDirectory(targetPath) {
  await ensureDir(targetPath)
  const probePath = path.join(targetPath, ".write-probe.tmp")
  await writeTextFile(probePath, "probe")
  await fsp.rm(probePath, { force: true })
}

export async function guardedWriteWithin(basePath, targetPath, content) {
  assertPathInside(basePath, targetPath)
  await writeTextFile(targetPath, content)
}

export async function guardedWriteJsonWithin(basePath, targetPath, value) {
  assertPathInside(basePath, targetPath)
  await writeJsonFile(targetPath, value)
}

export function fileSizeInBytes(targetPath) {
  if (!pathExistsSync(targetPath)) {
    return 0
  }
  return fs.statSync(targetPath).size
}

export async function readDirectoryDetailed(targetPath) {
  if (!(await pathExists(targetPath))) {
    return []
  }

  const entries = await fsp.readdir(targetPath, {
    withFileTypes: true
  })

  const details = []
  for (const entry of entries) {
    const absolute = path.join(targetPath, entry.name)
    const stat = await fsp.stat(absolute)
    details.push({
      name: entry.name,
      absolute,
      isDirectory: entry.isDirectory(),
      isFile: entry.isFile(),
      size: stat.size,
      mtimeMs: stat.mtimeMs
    })
  }

  return details.sort((a, b) => a.name.localeCompare(b.name))
}
