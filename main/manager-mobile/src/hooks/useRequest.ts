import type { Ref } from 'vue'

interface IUseRequestOptions<T> {
  /** Whether to execute immediately */
  immediate?: boolean
  /** Initial data */
  initialData?: T
}

interface IUseRequestReturn<T> {
  loading: Ref<boolean>
  error: Ref<boolean | Error>
  data: Ref<T | undefined>
  run: () => Promise<T | undefined>
}

/**
 * useRequest is a customized request hook for handling asynchronous requests and responses.
 * @param func A function that executes an asynchronous request, returns a Promise containing response data.
 * @param options Object containing request options {immediate, initialData}.
 * @param options.immediate Whether to execute request immediately, default is false.
 * @param options.initialData Initial data, default is undefined.
 * @returns Returns an object {loading, error, data, run}, containing request loading state, error info, response data, and function to manually trigger request.
 */
export default function useRequest<T>(
  func: () => Promise<IResData<T>>,
  options: IUseRequestOptions<T> = { immediate: false },
): IUseRequestReturn<T> {
  const loading = ref(false)
  const error = ref(false)
  const data = ref<T | undefined>(options.initialData) as Ref<T | undefined>
  const run = async () => {
    loading.value = true
    return func()
      .then((res) => {
        data.value = res.data
        error.value = false
        return data.value
      })
      .catch((err) => {
        error.value = err
        throw err
      })
      .finally(() => {
        loading.value = false
      })
  }

  options.immediate && run()
  return { loading, error, data, run }
}
