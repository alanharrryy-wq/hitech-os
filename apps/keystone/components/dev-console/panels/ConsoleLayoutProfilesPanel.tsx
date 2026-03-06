"use client";

import React, { useMemo, useState } from "react";
import styles from "../dev-console.module.css";
import type { DevConsoleFlags, DevConsoleToolId } from "../types";

const cls = (name: string) => styles[name] ?? "";

const WINDOW_STORAGE_KEY = "keystone.floatingWindow.dev-console";
const PROFILES_STORAGE_KEY = "keystone.devConsole.layoutProfiles";

type LayoutProfile = {
  id: string;
  name: string;
  savedAt: string;
  activeTool: DevConsoleToolId;
  flags: DevConsoleFlags;
  windowStateJson: string | null;
};

function readProfiles(): LayoutProfile[] {
  if (typeof window === "undefined") return [];

  try {
    const raw = localStorage.getItem(PROFILES_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as LayoutProfile[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeProfiles(profiles: LayoutProfile[]) {
  try {
    localStorage.setItem(PROFILES_STORAGE_KEY, JSON.stringify(profiles));
  } catch {
    // ignore
  }
}

type Props = {
  activeTool: DevConsoleToolId;
  setActiveTool: (tool: DevConsoleToolId) => void;
  flags: DevConsoleFlags;
  setFlags: React.Dispatch<React.SetStateAction<DevConsoleFlags>>;
};

export function ConsoleLayoutProfilesPanel({
  activeTool,
  setActiveTool,
  flags,
  setFlags
}: Props) {
  const [profiles, setProfiles] = useState<LayoutProfile[]>(() => readProfiles());
  const [profileName, setProfileName] = useState("Luxury Layout");

  const hasProfiles = profiles.length > 0;

  const sortedProfiles = useMemo(
    () => [...profiles].sort((a, b) => b.savedAt.localeCompare(a.savedAt)),
    [profiles]
  );

  const saveProfile = () => {
    if (typeof window === "undefined") return;

    const next: LayoutProfile = {
      id: crypto.randomUUID(),
      name: profileName.trim() || "Untitled Layout",
      savedAt: new Date().toISOString(),
      activeTool,
      flags,
      windowStateJson: localStorage.getItem(WINDOW_STORAGE_KEY)
    };

    const merged = [next, ...profiles];
    setProfiles(merged);
    writeProfiles(merged);
  };

  const loadProfile = (profile: LayoutProfile) => {
    setActiveTool(profile.activeTool);
    setFlags(profile.flags);

    try {
      if (profile.windowStateJson) {
        localStorage.setItem(WINDOW_STORAGE_KEY, profile.windowStateJson);
      } else {
        localStorage.removeItem(WINDOW_STORAGE_KEY);
      }
    } catch {
      // ignore
    }

    window.dispatchEvent(
      new CustomEvent("hitech:floating-window:restore", {
        detail: { id: "dev-console" }
      })
    );
  };

  const removeProfile = (profileId: string) => {
    const next = profiles.filter((item) => item.id !== profileId);
    setProfiles(next);
    writeProfiles(next);
  };

  return (
    <div className={cls("card")}>
      <div className={cls("cardTitle")}>Layout Profiles</div>
      <div className={cls("cardHint")}>
        Save and restore the console position, active tool, and runtime flags.
      </div>

      <div className={cls("split")}>
        <input
          className={cls("input")}
          value={profileName}
          onChange={(event) => setProfileName(event.currentTarget.value)}
          placeholder="Profile name"
        />

        <button type="button" className={cls("button")} onClick={saveProfile}>
          Save Current Layout
        </button>
      </div>

      {hasProfiles ? (
        <div className={cls("list")}>
          {sortedProfiles.map((profile) => (
            <div key={profile.id} className={cls("profileRow")}>
              <div>
                <div className={cls("cardTitle")}>{profile.name}</div>
                <div className={cls("cardHint")}>
                  {profile.activeTool} · {new Date(profile.savedAt).toLocaleString()}
                </div>
              </div>

              <button type="button" className={cls("button")} onClick={() => loadProfile(profile)}>
                Load
              </button>

              <button
                type="button"
                className={cls("button")}
                onClick={() => {
                  setProfileName(profile.name);
                }}
              >
                Copy Name
              </button>

              <button
                type="button"
                className={`${cls("button")} ${cls("buttonDanger")}`}
                onClick={() => removeProfile(profile.id)}
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className={cls("emptyState")}>
          <div className={cls("cardTitle")}>No profiles yet</div>
          <div className={cls("cardHint")}>
            Save one after moving the console to your favorite command-center position.
          </div>
        </div>
      )}
    </div>
  );
}
