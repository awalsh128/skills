/** Inputs of the action. */
export interface ActionInputs {
  readonly key: string;
}

/** Outputs of the action. */
export interface ActionOutputs {
  readonly cacheHit: boolean;
}

/** Cache operations the runner depends on. */
export interface Cache {
  restore(key: string): Promise<boolean>;
}

/**
 * Restores the cache for the given inputs.
 * @param inputs Parsed action inputs.
 * @param cache Cache dependency.
 * @returns The action outputs.
 */
export async function runAction(inputs: ActionInputs, cache: Cache): Promise<ActionOutputs> {
  const cacheHit = await cache.restore(inputs.key);
  return { cacheHit };
}
