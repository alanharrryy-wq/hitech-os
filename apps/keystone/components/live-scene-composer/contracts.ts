export interface LiveSceneComposerModule {
  readonly id: string;
  readonly title: string;
  readonly enabledByDefault: boolean;
}

export interface LiveSceneComposerRegistration {
  readonly modules: readonly LiveSceneComposerModule[];
}
